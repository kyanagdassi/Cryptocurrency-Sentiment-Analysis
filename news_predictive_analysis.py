import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime, timedelta

def load_data():
    print("Loading data files...")
    
    try:
        faith_scores = pd.read_csv('daily_faith_scores.csv')
        bitcoin_cap = pd.read_csv('bitcoin_market_cap_monthly.csv')
        
        print(f"Loaded {len(faith_scores)} days of faith scores")
        print(f"Loaded {len(bitcoin_cap)} days of Bitcoin market cap data")
        
        return faith_scores, bitcoin_cap
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def prepare_predictive_data(faith_scores, bitcoin_cap):
    print("\nPreparing data for analysis...")
    print("Testing: Same day market cap -> News sentiment")
    
    faith_scores['Date'] = pd.to_datetime(faith_scores['Date'])
    bitcoin_cap['Date'] = pd.to_datetime(bitcoin_cap['Date'])
    
    predictive_data = []
    
    for idx, faith_row in faith_scores.iterrows():
        faith_date = faith_row['Date']
        
        matching_market = bitcoin_cap[bitcoin_cap['Date'] == faith_date]
        
        if not matching_market.empty:
            market_cap = matching_market['Bitcoin Market Cap USD'].iloc[0]
            predictive_data.append({
                'News_Date': faith_date,
                'Faith_Score': faith_row['Faith Score'],
                'Same_Day_Date': faith_date,
                'Same_Day_Market_Cap': market_cap
            })
    
    df = pd.DataFrame(predictive_data)
    
    if len(df) > 0:
        df['Market_Cap_Change'] = df['Same_Day_Market_Cap'].pct_change() * 100
        df['Market_Cap_Change_Abs'] = abs(df['Market_Cap_Change'])
        
        print(f"Created {len(df)} same-day correlations")
        print(f"Date range: {df['News_Date'].min().date()} to {df['News_Date'].max().date()}")
        print(f"Average faith score: {df['Faith_Score'].mean():.2f}")
        print(f"Average same-day market cap: ${df['Same_Day_Market_Cap'].mean()/1e12:.3f}T")
    else:
        print("No matching dates found for analysis")
    
    return df

def calculate_predictive_correlations(data):
    print("\nCalculating correlations...")
    print("Analyzing: Same Day Market Cap -> Faith Score")
    
    if len(data) < 3:
        print("Not enough data for correlation analysis")
        return None
    
    faith_scores = data['Faith_Score']
    same_day_cap = data['Same_Day_Market_Cap']
    market_changes = data['Market_Cap_Change'].dropna()
    
    if len(market_changes) > 0:
        faith_for_changes = data['Faith_Score'].iloc[1:]
        pearson_corr_cap, pearson_p_cap = stats.pearsonr(faith_scores, same_day_cap)
        spearman_corr_cap, spearman_p_cap = stats.spearmanr(faith_scores, same_day_cap)
        
        pearson_corr_change, pearson_p_change = stats.pearsonr(faith_for_changes, market_changes)
        spearman_corr_change, spearman_p_change = stats.spearmanr(faith_for_changes, market_changes)
        
        print(f"\nCorrelation: Same Day Market Cap -> Faith Score")
        print(f"  Pearson: {pearson_corr_cap:.4f} (p-value: {pearson_p_cap:.4f})")
        print(f"  Spearman: {spearman_corr_cap:.4f} (p-value: {spearman_p_cap:.4f})")
        print(f"  R²: {pearson_corr_cap**2:.4f}")
        
        print(f"\nCorrelation: Same Day Market Cap Change -> Faith Score")
        print(f"  Pearson: {pearson_corr_change:.4f} (p-value: {pearson_p_change:.4f})")
        print(f"  Spearman: {spearman_corr_change:.4f} (p-value: {spearman_p_change:.4f})")
        print(f"  R²: {pearson_corr_change**2:.4f}")
        
        return {
            'market_cap': {
                'pearson_corr': pearson_corr_cap,
                'pearson_p': pearson_p_cap,
                'spearman_corr': spearman_corr_cap,
                'spearman_p': spearman_p_cap,
                'r_squared': pearson_corr_cap**2
            },
            'market_change': {
                'pearson_corr': pearson_corr_change,
                'pearson_p': pearson_p_change,
                'spearman_corr': spearman_corr_change,
                'spearman_p': spearman_p_change,
                'r_squared': pearson_corr_change**2
            }
        }
    else:
        print("No market change data available")
        return None

def analyze_prediction_accuracy(data, correlations):
    print("\nAnalyzing correlation strength...")
    
    if correlations is None:
        return
    
    print(f"\nCorrelation Analysis:")
    
    cap_corr = correlations['market_cap']['pearson_corr']
    cap_r2 = correlations['market_cap']['r_squared']
    cap_significant = correlations['market_cap']['pearson_p'] < 0.05
    
    if abs(cap_corr) > 0.5:
        cap_strength = "strong"
    elif abs(cap_corr) > 0.3:
        cap_strength = "moderate"
    elif abs(cap_corr) > 0.1:
        cap_strength = "weak"
    else:
        cap_strength = "very weak"
    
    cap_direction = "positive" if cap_corr > 0 else "negative"
    
    print(f"Market Cap Correlation:")
    print(f"  - {cap_strength.title()} {cap_direction} correlation")
    print(f"  - Explains {cap_r2*100:.1f}% of faith score variance")
    print(f"  - Statistically significant: {'Yes' if cap_significant else 'No'}")
    
    change_corr = correlations['market_change']['pearson_corr']
    change_r2 = correlations['market_change']['r_squared']
    change_significant = correlations['market_change']['pearson_p'] < 0.05
    
    if abs(change_corr) > 0.5:
        change_strength = "strong"
    elif abs(change_corr) > 0.3:
        change_strength = "moderate"
    elif abs(change_corr) > 0.1:
        change_strength = "weak"
    else:
        change_strength = "very weak"
    
    change_direction = "positive" if change_corr > 0 else "negative"
    
    print(f"\nMarket Change Correlation:")
    print(f"  - {change_strength.title()} {change_direction} correlation")
    print(f"  - Explains {change_r2*100:.1f}% of faith score variance")
    print(f"  - Statistically significant: {'Yes' if change_significant else 'No'}")
    
    print(f"\nOverall Assessment:")
    if cap_significant or change_significant:
        print("  - Previous day market movements show influence on news sentiment")
        if cap_corr > 0:
            print("  - Higher previous-day market cap correlates with higher faith scores")
        else:
            print("  - Higher previous-day market cap correlates with lower faith scores")
    else:
        print("  - Previous day market movements do not show significant influence on news sentiment")

def create_predictive_visualizations(data, correlations):
    print("\nCreating correlation analysis visualizations...")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    faith_scores = data['Faith_Score']
    same_day_cap = data['Same_Day_Market_Cap']
    news_dates = data['News_Date']
    ax1.scatter(same_day_cap, faith_scores, alpha=0.7, color='blue')
    ax1.set_xlabel('Same Day Bitcoin Market Cap (USD)')
    ax1.set_ylabel('Faith Score (News Day)')
    ax1.set_title('Same Day Market Cap vs News Sentiment')
    
    if correlations and correlations['market_cap']:
        corr_val = correlations['market_cap']['pearson_corr']
        ax1.set_title(f'Same Day Market Cap vs News Sentiment\n(Pearson r = {corr_val:.3f})')
        
        z = np.polyfit(same_day_cap, faith_scores, 1)
        p = np.poly1d(z)
        ax1.plot(same_day_cap, p(same_day_cap), "r-", linewidth=3, alpha=1.0)
    
    ax1.grid(True, alpha=0.3)
    ax2.plot(news_dates, faith_scores, marker='o', linewidth=3, color='green', label='Faith Score')
    ax2.set_xlabel('News Date')
    ax2.set_ylabel('Faith Score')
    ax2.set_title('News Sentiment Over Time')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    same_day_dates = data['Same_Day_Date']
    ax3.plot(same_day_dates, same_day_cap/1e12, marker='s', linewidth=3, color='orange', label='Same Day Market Cap')
    ax3.set_xlabel('Same Day Date')
    ax3.set_ylabel('Bitcoin Market Cap (Trillions USD)')
    ax3.set_title('Same Day Market Cap Over Time')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    ax4.plot(same_day_dates, same_day_cap/1e12, marker='s', linewidth=3, label='Same Day Market Cap (T)', color='orange')
    ax4_twin = ax4.twinx()
    ax4_twin.plot(news_dates, faith_scores, marker='o', linewidth=3, label='Faith Score (News Day)', color='green')
    ax4.set_xlabel('Date')
    ax4.set_ylabel('Same Day Market Cap (Trillions USD)', color='orange')
    ax4_twin.set_ylabel('Faith Score', color='green')
    ax4.set_title('Same Day Market Cap vs News Sentiment Timeline')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('news_predictive_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved correlation analysis plots to 'news_predictive_analysis.png'")
    
    try:
        plt.show()
    except:
        print("Interactive display not available, but plots saved to file")

def analyze_high_confidence_predictions(data, correlations):
    print("\nAnalyzing high-confidence correlations...")
    
    if correlations is None:
        return
    faith_mean = data['Faith_Score'].mean()
    faith_std = data['Faith_Score'].std()
    
    high_faith_threshold = faith_mean + faith_std
    low_faith_threshold = faith_mean - faith_std
    
    high_faith_days = data[data['Faith_Score'] >= high_faith_threshold]
    low_faith_days = data[data['Faith_Score'] <= low_faith_threshold]
    
    print(f"High faith days (>{high_faith_threshold:.1f}): {len(high_faith_days)} days")
    print(f"Low faith days (<{low_faith_threshold:.1f}): {len(low_faith_days)} days")
    
    if len(high_faith_days) > 0:
        avg_same_cap_high = high_faith_days['Same_Day_Market_Cap'].mean()
        print(f"Average same-day market cap for high faith: ${avg_same_cap_high/1e12:.3f}T")
    
    if len(low_faith_days) > 0:
        avg_same_cap_low = low_faith_days['Same_Day_Market_Cap'].mean()
        print(f"Average same-day market cap for low faith: ${avg_same_cap_low/1e12:.3f}T")
    data_with_changes = data.dropna(subset=['Market_Cap_Change'])
    
    if len(data_with_changes) > 0:
        faith_mean_changes = data_with_changes['Faith_Score'].mean()
        faith_std_changes = data_with_changes['Faith_Score'].std()
        
        high_faith_changes = data_with_changes[data_with_changes['Faith_Score'] >= faith_mean_changes + faith_std_changes]
        low_faith_changes = data_with_changes[data_with_changes['Faith_Score'] <= faith_mean_changes - faith_std_changes]
        
        if len(high_faith_changes) > 0:
            avg_change_high = high_faith_changes['Market_Cap_Change'].mean()
            print(f"Average same-day market change for high faith: {avg_change_high:+.2f}%")
        
        if len(low_faith_changes) > 0:
            avg_change_low = low_faith_changes['Market_Cap_Change'].mean()
            print(f"Average same-day market change for low faith: {avg_change_low:+.2f}%")

def generate_predictive_summary(data, correlations):
    print("\n" + "="*60)
    print("NEWS SENTIMENT CORRELATION ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nAnalysis Setup:")
    print(f"- Same day market cap -> News sentiment on Day N")
    print(f"- Analysis period: {data['News_Date'].min().date()} to {data['News_Date'].max().date()}")
    print(f"- Number of correlations: {len(data)}")
    
    print(f"\nData Summary:")
    print(f"- Average faith score: {data['Faith_Score'].mean():.2f}")
    print(f"- Average same-day market cap: ${data['Same_Day_Market_Cap'].mean()/1e12:.3f}T")
    
    if correlations:
        cap_corr = correlations['market_cap']['pearson_corr']
        change_corr = correlations['market_change']['pearson_corr']
        
        print(f"\nCorrelation Strength:")
        print(f"- Market Cap Correlation R²: {correlations['market_cap']['r_squared']:.4f}")
        print(f"- Market Change Correlation R²: {correlations['market_change']['r_squared']:.4f}")
        
        print(f"\nKey Findings:")
        if abs(cap_corr) > 0.3:
            print("- Same day market cap shows moderate influence on news sentiment")
        elif abs(cap_corr) > 0.1:
            print("- Same day market cap shows weak influence on news sentiment")
        else:
            print("- Same day market cap shows very weak influence on news sentiment")
        
        if cap_corr > 0:
            print("- Higher same-day market cap correlates with higher faith scores")
        else:
            print("- Higher same-day market cap correlates with lower faith scores")
        
        if correlations['market_cap']['pearson_p'] < 0.05:
            print("- Statistical significance: YES - Results are reliable")
        else:
            print("- Statistical significance: NO - Results may be due to chance")
    
    print(f"\nImplications:")
    if correlations and correlations['market_cap']['pearson_p'] < 0.05:
        print("- Market movements influence news sentiment")
        print("- News sentiment may be reactive rather than predictive")
    else:
        print("- Market movements do not significantly influence news sentiment")
        print("- News sentiment may be independent of recent market performance")
    
    print("\n" + "="*60)

def main():
    print("CRYPTOCURRENCY NEWS SENTIMENT CORRELATION ANALYSIS")
    print("="*60)
    print("Testing: Same Day Market Cap -> News Sentiment")
    
    faith_scores, bitcoin_cap = load_data()
    
    if faith_scores is None or bitcoin_cap is None:
        print("Failed to load data files. Please ensure both CSV files exist.")
        return
    
    data = prepare_predictive_data(faith_scores, bitcoin_cap)
    
    if len(data) == 0:
        print("No data available for predictive analysis.")
        return
    
    correlations = calculate_predictive_correlations(data)
    analyze_prediction_accuracy(data, correlations)
    create_predictive_visualizations(data, correlations)
    analyze_high_confidence_predictions(data, correlations)
    generate_predictive_summary(data, correlations)
    
    data.to_csv('news_predictive_analysis_data.csv', index=False)
    print(f"\nPredictive analysis data saved to 'news_predictive_analysis_data.csv'")

if __name__ == "__main__":
    main()
