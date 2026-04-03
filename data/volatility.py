def calc_atr(df, period=14):
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    tr = df[['H-L','H-PC','L-PC']].max(axis=1)
    return tr.rolling(period).mean().iloc[-1]
