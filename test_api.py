from app import app
c = app.test_client()
r = c.get("/"); assert r.status_code == 200 and b"Heart disease model demo" in r.data
assert c.get("/health").get_json() == {"status": "ok"} and c.get("/api/info").get_json()["n_total"] == 500
ok = dict(age=55, sex="Male", blood_pressure=130, cholesterol=220, bmi=29, smoker="Yes", diabetes="No", physical_activity=2, family_history="No", stress_level=5)
o = c.post("/predict", json=ok).get_json(); assert 0 < o["probability"] < 1 and o["warnings"] == []; print(o)
assert c.post("/predict", json={**ok, "age": 150}).status_code == 400
assert c.post("/predict", json={**ok, "smoker": "maybe"}).status_code == 400
assert c.post("/predict", json={**ok, "bmi": "x"}).status_code == 400
assert c.post("/predict", json={}).status_code == 400
w = c.post("/predict", json={**ok, "age": 95}).get_json(); assert w["warnings"], w
b = c.post("/predict_batch", json={"rows": [ok, {**ok, "sex": "female"}]}).get_json(); assert len(b["results"]) == 2
e = c.post("/predict_batch", json={"rows": [ok, {**ok, "age": -1}]}); assert e.status_code == 400 and "Row 2" in e.get_json()["error"]
assert c.post("/predict_batch", json={"rows": []}).status_code == 400
print("all tests passed")
