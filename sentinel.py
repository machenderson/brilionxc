import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

class CryptoPulseSentinel:
    """
    BrilionX Crypto Tools: CryptoPulse-Sentinel
    A modular suite for monitoring and auditing Crypto Fat-Finger errors.
    """
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = pd.DataFrame()
        self.anomalies = pd.DataFrame()

    # --- MODULE 1: Data Ingestion ---
    def fetch_market_data(self, period="2d", interval="1m"):
        """Fetches high-frequency crypto data from global exchanges."""
        print(f"[*] BrilionX Sentinel: Ingesting live feed for {self.ticker}...")
        self.data = yf.download(self.ticker, period=period, interval=interval)
        if self.data.empty:
            raise ConnectionError("Failed to retrieve market data.")
        return self.data

    # --- MODULE 2: Quantitative Analysis & Calculation ---
    def _calculate_metrics(self, window=30):
        """Calculates volatility-adjusted metrics and Rolling Z-Scores."""
        df = self.data.copy()
        
        # Calculate 'Price Needle' (High-Low Spread %)
        df['needle_pct'] = (df['High'] - df['Low']) / df['Low']
        
        # Calculate Rolling Mean and Std Dev for the spread
        df['rolling_mean'] = df['needle_pct'].rolling(window=window).mean()
        df['rolling_std'] = df['needle_pct'].rolling(window=window).std()
        
        # Z-Score: (Current Spread - Mean) / StdDev
        df['z_score'] = (df['needle_pct'] - df['rolling_mean']) / df['rolling_std']
        return df

    # --- MODULE 3: Monitoring & Identification ---
    def identify_fat_fingers(self, z_threshold=8, vol_multiplier=5):
        """
        Monitors the feed for statistical outliers.
        Crypto requires higher thresholds (Z-Score > 8) to avoid 'Normal' volatility.
        """
        df = self._calculate_metrics()
        avg_vol = df['Volume'].rolling(window=30).mean()
        
        # Condition: Massive price needle AND unusual volume spike
        mask = (df['z_score'] > z_threshold) & (df['Volume'] > avg_vol * vol_multiplier)
        
        self.anomalies = df[mask].copy()
        return self.anomalies

    # --- MODULE 4: Export & Audit ---
    def export_report(self, format="csv"):
        """Generates a forensic audit report for compliance or strategy adjustment."""
        if self.anomalies.empty:
            print("[!] No fat-finger anomalies detected. Export cancelled.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Sentinel_Audit_{self.ticker.replace('-', '_')}_{timestamp}.{format}"
        
        if format == "csv":
            self.anomalies.to_csv(filename)
        elif format == "json":
            self.anomalies.to_json(filename, orient="records", date_format="iso")
            
        print(f"[✓] BrilionX Audit Report generated: {filename}")

# --- BrilionX Execution Pipeline ---
if __name__ == "__main__":
    # Example: Monitoring Bitcoin (BTC-USD) or Ethereum (ETH-USD)
    sentinel = CryptoPulseSentinel("BTC-USD")
    
    try:
        # Step 1: Ingest
        sentinel.fetch_market_data()
        
        # Step 2 & 3: Analyze & Detect
        # We use a high Z-Score because Crypto is naturally 'jumpy'
        results = sentinel.identify_fat_fingers(z_threshold=10, vol_multiplier=6)
        
        print("\n--- Sentinel Live Monitoring Report ---")
        if not results.empty:
            print(f"CRITICAL: {len(results)} Fat-Finger event(s) identified!")
            print(results[['High', 'Low', 'Volume', 'z_score']].tail())
            
            # Step 4: Export
            sentinel.export_report(format="csv")
        else:
            print("Status: System Nominal. No execution errors detected.")
            
    except Exception as e:
        print(f"[System Error]: {e}")