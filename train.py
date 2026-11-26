import json, numpy as np, pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split, cross_validate, RepeatedStratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix

df = pd.read_excel("hospital_synthetic_dataset.xlsx")
y = df.pop("heart_disease")
NUM = ["age","blood_pressure","cholesterol","bmi","physical_activity","stress_level"]
CAT = ["sex","smoker","diabetes","family_history"]
pre = lambda: ColumnTransformer([("n", StandardScaler(), NUM), ("c", OneHotEncoder(drop="if_binary"), CAT)])
pipe = lambda m: make_pipeline(pre(), m)

X_tr, X_te, y_tr, y_te = train_test_split(df, y, test_size=.2, stratify=y, random_state=42)
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
models = {"Baseline (always majority class)": DummyClassifier(strategy="most_frequent"),
          "Logistic regression": LogisticRegression(max_iter=2000), "KNN (k = 15)": KNeighborsClassifier(15),
          "Random forest": RandomForestClassifier(300, min_samples_leaf=5, random_state=42),
          "Gradient boosting": GradientBoostingClassifier(random_state=42)}
rows = []
for n, m in models.items():
    r = cross_validate(pipe(m), X_tr, y_tr, cv=cv, scoring=["accuracy","roc_auc"])
    rows.append(dict(name=n, acc=r["test_accuracy"].mean(), acc_sd=r["test_accuracy"].std(), auc=r["test_roc_auc"].mean(), auc_sd=r["test_roc_auc"].std()))

# held-out test for the chosen model (logistic regression: simple, interpretable, exportable)
m = pipe(LogisticRegression(max_iter=2000)).fit(X_tr, y_tr)
pr = m.predict_proba(X_te)[:, 1]; pred = (pr >= .5).astype(int)
acc = accuracy_score(y_te, pred); base = max(y_te.mean(), 1 - y_te.mean()) if y_tr.mean() > .5 else 1 - y_te.mean()
base = y_te.mean() if y_tr.mean() > .5 else 1 - y_te.mean()      # majority class of the TRAINING set
auc = roc_auc_score(y_te, pr); cm = confusion_matrix(y_te, pred, labels=[0, 1]).tolist()
z = 1.96; n = len(y_te); ci = ((acc + z*z/(2*n) - z*np.sqrt(acc*(1-acc)/n + z*z/(4*n*n))) / (1 + z*z/n), (acc + z*z/(2*n) + z*np.sqrt(acc*(1-acc)/n + z*z/(4*n*n))) / (1 + z*z/n))

# single-feature significance tests on all 500 rows
pv = {}
for c in NUM: pv[c] = stats.ttest_ind(df[c][y == 1], df[c][y == 0]).pvalue
for c in CAT: pv[c] = stats.chi2_contingency(pd.crosstab(df[c], y))[1]
best = min(pv, key=pv.get)

# final model on all 500 rows + bootstrap CIs for coefficients
final = pipe(LogisticRegression(max_iter=2000)).fit(df, y); sc, lr, enc = final[0].named_transformers_["n"], final[1], final[0].named_transformers_["c"]
names = NUM + [f"{c}_{enc.categories_[i][1]}" for i, c in enumerate(CAT)]
rng = np.random.default_rng(42); boots = []
for _ in range(300):
    i = rng.integers(0, len(df), len(df)); boots.append(pipe(LogisticRegression(max_iter=2000)).fit(df.iloc[i], y.iloc[i])[1].coef_[0])
lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
effects = [dict(name=n_, coef=float(c), lo=float(a), hi=float(b)) for n_, c, a, b in zip(names, lr.coef_[0], lo, hi)]

json.dump(dict(num=NUM, cat=CAT, cats={c: [str(v) for v in enc.categories_[i]] for i, c in enumerate(CAT)},
    mean=sc.mean_.tolist(), scale=sc.scale_.tolist(), coef=lr.coef_[0].tolist(), intercept=float(lr.intercept_[0]),
    base_rate=float(y.mean()), range={c: [float(df[c].min()), float(df[c].max())] for c in NUM}), open("model.json", "w"))
json.dump(dict(n_total=len(df), n_train=len(X_tr), n_test=len(X_te), positive_rate=float(y.mean()), models=rows,
    test=dict(accuracy=acc, baseline=float(base), auc=auc, confusion=cm, ci=list(ci)), effects=effects,
    best_feature=best, best_p=float(pv[best]), n_tests=len(pv), bonferroni=0.05 / len(pv)), open("metrics.json", "w"), indent=1)

print(pd.DataFrame(rows).round(3).to_string(index=False))
print(f"\nTEST  acc {acc:.3f} (95% CI {ci[0]:.2f}-{ci[1]:.2f})  baseline {base:.3f}  AUC {auc:.3f}  confusion {cm}")
print(f"smallest single-feature p-value: {best} p={pv[best]:.4f}  (Bonferroni threshold {0.05/len(pv):.4f})")
print(pd.DataFrame(effects).round(3).to_string(index=False))
