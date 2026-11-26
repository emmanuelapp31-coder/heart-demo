# Heart disease model demo

Flask API (app.py) + embedded page (page.py). The logistic regression is stored in model.json
and evaluated in plain Python, so only Flask is needed at runtime.

NOT a medical tool: the dataset is synthetic and the model is no better than guessing.

    pip install flask && python app.py      # http://localhost:5000

Deploy on Vercel: put these files at the root of a GitHub repo, then Add New > Project > Deploy.
Retrain: pip install scikit-learn pandas openpyxl scipy; python train.py (rewrites model.json, metrics.json).
