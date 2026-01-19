import pandas as pd

# Check current features.csv
df = pd.read_csv('data/features.csv')
print('Date column exists:', 'date' in df.columns)
print(f'Total rows: {len(df)}')
print(f'Columns: {list(df.columns)[:15]}')

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    print(f'\nDate range: {df["date"].min()} to {df["date"].max()}')
    print(f'\nMost recent 10 dates:')
    print(df['date'].nlargest(10).values)
    
    # Show sample of most recent data
    print(f'\nMost recent matches:')
    recent = df.nlargest(5, 'date')[['player', 'date', 'runs_scored', 'strike_rate', 'opponent', 'venue']]
    print(recent.to_string())
