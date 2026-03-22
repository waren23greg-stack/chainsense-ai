import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from utils.csv_validator import detect_column_roles

class AnalyticsService:
    def __init__(self, df):
        self.df   = df.copy()
        self.df.columns = [c.lower().strip() for c in self.df.columns]
        self.cols = list(self.df.columns)
        self.roles = detect_column_roles(self.df)

    def _col(self, role): return self.roles.get(role)

    def get_kpis(self):
        k = {"row_count": len(self.df)}
        rev = self._col("revenue")
        if rev:
            k["total_revenue"]   = round(float(self.df[rev].sum()), 2)
            k["avg_order_value"] = round(float(self.df[rev].mean()), 2)
        st = self._col("status")
        if st:
            counts = self.df[st].value_counts().to_dict()
            k["status_breakdown"]  = {str(a): int(b) for a, b in counts.items()}
            cancelled              = sum(v for a, v in counts.items() if str(a).lower() in ["cancelled","canceled"])
            k["cancellation_rate"] = round(cancelled / len(self.df) * 100, 1)
        d = self._col("delay")
        if d:
            k["avg_delay_days"] = round(float(self.df[d].mean()), 2)
            k["max_delay_days"] = int(self.df[d].max())
        s = self._col("supplier")
        if s: k["unique_suppliers"] = int(self.df[s].nunique())
        p = self._col("product")
        if p: k["unique_products"]  = int(self.df[p].nunique())
        return k

    def get_revenue_trend(self):
        dc, rc = self._col("date"), self._col("revenue")
        if not dc or not rc: return []
        df = self.df[[dc, rc]].copy()
        df[dc] = pd.to_datetime(df[dc], errors="coerce")
        df     = df.dropna(subset=[dc])
        df["month"] = df[dc].dt.to_period("M")
        m = df.groupby("month")[rc].sum().reset_index()
        m["month"] = m["month"].astype(str)
        return m.rename(columns={rc: "revenue"}).to_dict(orient="records")

    def get_forecast(self, periods=3):
        trend = self.get_revenue_trend()
        if len(trend) < 4: return {"error": "Need at least 4 months of data."}
        rev = np.array([t["revenue"] for t in trend])
        X   = np.arange(len(rev)).reshape(-1, 1)
        m   = LinearRegression().fit(X, rev)
        lp  = pd.Period(trend[-1]["month"], freq="M")
        fc  = [{"month": str(lp + (i+1)), "revenue": round(float(v), 2), "forecast": True}
               for i, v in enumerate(m.predict(np.arange(len(rev), len(rev)+periods).reshape(-1,1)))]
        return {"historical": trend, "forecast": fc, "r2_score": round(float(m.score(X, rev)), 3), "trend_direction": "up" if m.coef_[0] > 0 else "down"}

    def get_supplier_scorecard(self, top_n=10):
        sc = self._col("supplier")
        if not sc: return []
        agg  = {}
        rev  = self._col("revenue")
        if rev: agg[rev] = "sum"
        d    = self._col("delay")
        if d:   agg[d]   = "mean"
        base = self.df.groupby(sc).size().rename("order_count").to_frame()
        if agg:
            extra = self.df.groupby(sc).agg(agg).rename(columns={rev: "total_revenue", d: "avg_delay"} if rev and d else ({rev: "total_revenue"} if rev else {d: "avg_delay"}))
            base  = base.join(extra)
        st = self._col("status")
        if st:
            delivered = self.df[self.df[st].str.lower().isin(["delivered","completed"])].groupby(sc).size()
            base["on_time_rate"] = (delivered / self.df.groupby(sc).size()).fillna(0).round(3)
        if "total_revenue" in base.columns:
            base = base.sort_values("total_revenue", ascending=False)
        return base.head(top_n).fillna(0).reset_index().to_dict(orient="records")

    def get_risk_alerts(self):
        alerts = []
        st = self._col("status")
        if st:
            total     = len(self.df)
            cancelled = self.df[st].str.lower().isin(["cancelled","canceled"]).sum()
            rate      = cancelled / total * 100 if total else 0
            if rate > 15: alerts.append({"level":"high","type":"cancellation_rate","message":f"Cancellation rate is {rate:.1f}% — investigate root cause.","value":round(rate,1)})
        d = self._col("delay")
        if d:
            avg = self.df[d].mean()
            if avg > 7: alerts.append({"level":"medium","type":"avg_delay","message":f"Average shipment delay is {avg:.1f} days.","value":round(avg,1)})
            severe = int((self.df[d] > 14).sum())
            if severe: alerts.append({"level":"high","type":"extreme_delays","message":f"{severe} shipments delayed over 14 days.","value":severe})
        sk, rk = self._col("stock"), self._col("reorder")
        if sk and rk:
            at_risk = int((self.df[sk] < self.df[rk]).sum())
            if at_risk: alerts.append({"level":"high","type":"stockout_risk","message":f"{at_risk} products below reorder point.","value":at_risk})
        return alerts

    def build_ai_context(self):
        k, a, s, f = self.get_kpis(), self.get_risk_alerts(), self.get_supplier_scorecard(5), self.get_forecast()
        lines = ["=== SUPPLY CHAIN DATA SUMMARY ===", f"Records: {k.get('row_count')}", f"Columns: {', '.join(self.cols)}", "", "--- KEY METRICS ---"]
        if "total_revenue"   in k: lines += [f"Total revenue:    ${k['total_revenue']:,.2f}", f"Avg order value:  ${k['avg_order_value']:,.2f}"]
        if "cancellation_rate" in k: lines.append(f"Cancellation rate: {k['cancellation_rate']}%")
        if "avg_delay_days"  in k: lines.append(f"Avg delay:         {k['avg_delay_days']} days")
        if "unique_suppliers" in k: lines.append(f"Active suppliers:  {k['unique_suppliers']}")
        if a: lines += ["", "--- RISK ALERTS ---"] + [f"[{x['level'].upper()}] {x['message']}" for x in a]
        if s: lines += ["", "--- TOP 5 SUPPLIERS ---"] + [str(x) for x in s]
        if "forecast" in f: lines += ["", "--- REVENUE FORECAST ---"] + [f"  {x['month']}: ${x['revenue']:,.0f}" for x in f["forecast"]] + [f"R²={f['r2_score']} Trend={f['trend_direction']}"]
        return "\n".join(lines)
