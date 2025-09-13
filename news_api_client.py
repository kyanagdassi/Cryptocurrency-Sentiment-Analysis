from newsapi import NewsApiClient
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import time

newsapi = NewsApiClient(api_key="624a9db7179d49a180ccf16e70d43f79")

def get_crypto_news(query="cryptocurrency", language="en", sort_by="publishedAt"):
    try:
        articles = newsapi.get_everything(
            q=query,
            language=language,
            sort_by=sort_by,
            page_size=100
        )
        return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None

def get_crypto_headlines(country="us", category="business"):
    try:
        headlines = newsapi.get_top_headlines(
            category=category,
            country=country,
            page_size=100
        )
        return headlines
    except Exception as e:
        print(f"Error fetching headlines: {e}")
        return None

def analyze_news_sentiment(articles):
    if not articles or not articles.get('articles'):
        return {"error": "No articles to analyze"}
    
    sentiment_results = {
        "total_articles": len(articles['articles']),
        "positive_keywords": ["trust", "faith", "confidence", "adoption", "mainstream", "institutional", "secure", "reliable", "future", "revolutionary", "breakthrough", "innovation", "legitimate", "accepted", "embraced"],
        "negative_keywords": ["distrust", "doubt", "skepticism", "scam", "fraud", "bubble", "risky", "volatile", "unreliable", "suspicious", "questionable", "doubtful", "uncertain", "wary", "cautious"],
        "neutral_keywords": ["stable", "hold", "consolidate", "sideways", "mixed", "divided", "debate", "discussion", "analysis", "evaluation", "assessment"]
    }
    
    return sentiment_results

def get_total_market_cap_history(days=30):
    try:
        print("Fetching real historical market cap data from top cryptocurrencies...")
        
        top_coins = get_top_cryptocurrencies()
        if not top_coins:
            print("Failed to get top cryptocurrencies, using fallback...")
            return get_current_market_cap_with_trend(days)
        
        all_historical_data = {}
        
        for coin_id in top_coins[:20]:
            print(f"Fetching data for {coin_id}...")
            coin_data = get_coin_historical_data(coin_id, days)
            if coin_data:
                all_historical_data[coin_id] = coin_data
        
        if not all_historical_data:
            print("No historical data available, using fallback...")
            return get_current_market_cap_with_trend(days)
        
        dates = []
        total_market_caps = []
        
        first_coin = list(all_historical_data.keys())[0]
        first_coin_data = all_historical_data[first_coin]
        
        for i, (timestamp, _) in enumerate(first_coin_data):
            date = datetime.fromtimestamp(timestamp / 1000)
            dates.append(date)
            
            daily_total = 0
            for coin_id, coin_data in all_historical_data.items():
                if i < len(coin_data):
                    daily_total += coin_data[i][1]
            
            total_market_caps.append(daily_total)
        
        current_tmc = total_market_caps[-1] if total_market_caps else 0
        
        print(f"Successfully calculated total market cap from {len(all_historical_data)} cryptocurrencies")
        print(f"Current total market cap: ${current_tmc/1e12:.3f}T")
        
        return {
            'dates': dates,
            'market_caps': total_market_caps,
            'current_tmc': current_tmc
        }
        
    except Exception as e:
        print(f"Error fetching real historical data: {e}")
        print("Falling back to current market cap with trend...")
        return get_current_market_cap_with_trend(days)

def get_top_cryptocurrencies():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 50,
            'page': 1
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return [coin['id'] for coin in data]
        
    except Exception as e:
        print(f"Error fetching top cryptocurrencies: {e}")
        return None

def get_coin_historical_data(coin_id, days=30):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': str(days),
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data['market_caps']
        
    except Exception as e:
        print(f"Error fetching data for {coin_id}: {e}")
        return None

def get_current_market_cap_with_trend(days=30):
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        current_tmc = data['data']['total_market_cap']['usd']
        change_24h = data['data']['market_cap_change_percentage_24h_usd']
        
        dates = []
        market_caps = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            dates.append(date)
            
            days_ago = days - i - 1
            trend_factor = 1 + (change_24h / 100) * (days_ago / 30)
            variation = 1 + (0.02 * (i % 7 - 3) / 7)
            historical_tmc = current_tmc * trend_factor * variation
            market_caps.append(historical_tmc)
        
        print(f"Using current market cap: ${current_tmc/1e12:.3f}T")
        print(f"24h change: {change_24h:.2f}%")
        print("Note: Historical data is estimated based on current trends")
        
        return {
            'dates': dates,
            'market_caps': market_caps,
            'current_tmc': current_tmc
        }
        
    except Exception as e:
        print(f"Error fetching current market cap data: {e}")
        return None

def get_bitcoin_market_cap_proxy(days=30):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': str(days),
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        market_cap_data = data['market_caps']
        
        dates = []
        market_caps = []
        
        for item in market_cap_data:
            timestamp = item[0] / 1000
            date = datetime.fromtimestamp(timestamp)
            dates.append(date)
            
            btc_market_cap = item[1]
            estimated_total_market_cap = btc_market_cap * 2.5
            market_caps.append(estimated_total_market_cap)
        
        current_tmc = market_caps[-1] if market_caps else 0
        
        print(f"Note: Using Bitcoin market cap * 2.5 as proxy for total market cap")
        print(f"Bitcoin dominance is typically 40-60%, so this is an approximation")
        
        return {
            'dates': dates,
            'market_caps': market_caps,
            'current_tmc': current_tmc
        }
        
    except Exception as e:
        print(f"Error fetching Bitcoin market cap data: {e}")
        return None

def graph_market_cap_history(market_cap_data):
    if not market_cap_data:
        print("No market cap data to graph")
        return
    
    plt.figure(figsize=(12, 6))
    plt.plot(market_cap_data['dates'], market_cap_data['market_caps'], 
             linewidth=2, color='#1f77b4', marker='o', markersize=3)
    
    plt.title('Cryptocurrency Total Market Cap - Last 30 Days', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Total Market Cap (USD)', fontsize=12)
    
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e12:.2f}T'))
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.xticks(rotation=45)
    
    plt.grid(True, alpha=0.3)
    
    current_value = market_cap_data['current_tmc']
    plt.annotate(f'Current: ${current_value/1e12:.2f}T', 
                xy=(market_cap_data['dates'][-1], current_value),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    
    plt.savefig('crypto_market_cap_30days.png', dpi=300, bbox_inches='tight')
    print("Graph saved as 'crypto_market_cap_30days.png'")
    
    try:
        plt.show()
    except:
        print("Interactive display not available, but graph saved to file")
    
    min_cap = min(market_cap_data['market_caps'])
    max_cap = max(market_cap_data['market_caps'])
    avg_cap = sum(market_cap_data['market_caps']) / len(market_cap_data['market_caps'])
    
    print(f"\nMarket Cap Summary (Last 30 Days):")
    print(f"Current: ${current_value/1e12:.2f}T")
    print(f"Minimum: ${min_cap/1e12:.2f}T")
    print(f"Maximum: ${max_cap/1e12:.2f}T")
    print(f"Average: ${avg_cap/1e12:.2f}T")
    print(f"Change: {((current_value - market_cap_data['market_caps'][0]) / market_cap_data['market_caps'][0] * 100):+.2f}%")

def get_articles_for_specific_dates(query="cryptocurrency", days_back=30):
    try:
        all_articles = []
        
        for i in range(days_back):
            target_date = datetime.now() - timedelta(days=i)
            date_str = target_date.strftime('%Y-%m-%d')
            
            print(f"Fetching articles for {date_str}...")
            
            try:
                search_terms = [query, "bitcoin", "crypto"]
                
                for search_term in search_terms:
                    try:
                        articles = newsapi.get_everything(
                            q=search_term,
                            language='en',
                            sort_by='publishedAt',
                            from_param=date_str,
                            to=date_str,
                            page_size=50
                        )
                        
                        if articles and articles.get('articles'):
                            day_articles = []
                            for article in articles['articles']:
                                try:
                                    pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                                    if pub_date.date().isoformat() == date_str:
                                        day_articles.append(article)
                                except:
                                    continue
                            
                            if day_articles:
                                all_articles.extend(day_articles)
                                print(f"  Found {len(day_articles)} articles for {date_str} with '{search_term}'")
                        
                        time.sleep(0.3)
                        
                    except Exception as e:
                        print(f"  Error fetching articles for {date_str} with '{search_term}': {e}")
                        continue
                
            except Exception as e:
                print(f"Error fetching articles for {date_str}: {e}")
                continue
            
            if i > 5 and len([a for a in all_articles if datetime.fromisoformat(a['publishedAt'].replace('Z', '+00:00')).date().isoformat() == date_str]) == 0:
                print(f"No articles found for {date_str}, stopping early")
                break
        
        unique_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article.get('url') and article['url'] not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(article['url'])
        
        print(f"Total unique articles found: {len(unique_articles)}")
        return unique_articles
            
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []

def analyze_article_sentiment(article_text):
    positive_keywords = ["trust", "faith", "confidence", "adoption", "mainstream", "institutional", "secure", "reliable", "future", "revolutionary", "breakthrough", "innovation", "legitimate", "accepted", "embraced"]
    negative_keywords = ["distrust", "doubt", "skepticism", "scam", "fraud", "bubble", "risky", "volatile", "unreliable", "suspicious", "questionable", "doubtful", "uncertain", "wary", "cautious"]
    neutral_keywords = ["stable", "hold", "consolidate", "sideways", "mixed", "divided", "debate", "discussion", "analysis", "evaluation", "assessment"]
    
    text_lower = article_text.lower()
    
    positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
    neutral_count = sum(1 for keyword in neutral_keywords if keyword in text_lower)
    
    return {
        'positive': positive_count,
        'negative': negative_count,
        'neutral': neutral_count,
        'total': positive_count + negative_count + neutral_count
    }

def calculate_daily_faith_scores(articles):
    daily_sentiment = {}
    date_counts = {}
    
    print("Processing articles and analyzing sentiment...")
    
    for i, article in enumerate(articles):
        try:
            pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
            date_str = pub_date.date().isoformat()
            
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
            
            article_text = f"{article['title']} {article.get('description', '')}"
            
            sentiment = analyze_article_sentiment(article_text)
            
            if date_str not in daily_sentiment:
                daily_sentiment[date_str] = {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'total_articles': 0
                }
            
            daily_sentiment[date_str]['positive'] += sentiment['positive']
            daily_sentiment[date_str]['negative'] += sentiment['negative']
            daily_sentiment[date_str]['neutral'] += sentiment['neutral']
            daily_sentiment[date_str]['total_articles'] += 1
            
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            continue
    
    print(f"\nDate distribution of articles:")
    for date_str in sorted(date_counts.keys()):
        print(f"  {date_str}: {date_counts[date_str]} articles")
    
    daily_scores = {}
    for date_str, sentiment_data in daily_sentiment.items():
        total_keywords = sentiment_data['positive'] + sentiment_data['negative'] + sentiment_data['neutral']
        
        if total_keywords == 0:
            faith_score = 50
        else:
            positive_weight = sentiment_data['positive'] * 100
            negative_weight = sentiment_data['negative'] * 0
            neutral_weight = sentiment_data['neutral'] * 50
            
            faith_score = (positive_weight + negative_weight + neutral_weight) / total_keywords
        
        daily_scores[date_str] = {
            'faith_score': faith_score,
            'positive_count': sentiment_data['positive'],
            'negative_count': sentiment_data['negative'],
            'neutral_count': sentiment_data['neutral'],
            'total_articles': sentiment_data['total_articles']
        }
        
        print(f"\n{date_str} Analysis:")
        print(f"  Articles: {sentiment_data['total_articles']}")
        print(f"  Positive keywords: {sentiment_data['positive']}")
        print(f"  Negative keywords: {sentiment_data['negative']}")
        print(f"  Neutral keywords: {sentiment_data['neutral']}")
        print(f"  Faith Score: {faith_score:.2f}")
    
    return daily_scores

def save_daily_faith_scores(daily_scores, filename="daily_faith_scores.csv"):
    import pandas as pd
    
    data = []
    for date_str in sorted(daily_scores.keys()):
        score_data = daily_scores[date_str]
        data.append({
            'Date': date_str,
            'Faith Score': score_data['faith_score']
        })
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    
    print(f"\nSaved daily faith scores to {filename}")
    print(f"Total days with data: {len(df)}")
    
    if len(df) > 0:
        print(f"Average faith score: {df['Faith Score'].mean():.2f}")
        print(f"Min faith score: {df['Faith Score'].min():.2f}")
        print(f"Max faith score: {df['Faith Score'].max():.2f}")
    
    return df

if __name__ == "__main__":
    print("NewsAPI Client initialized successfully!")
    print("="*60)
    print("FETCHING CRYPTOCURRENCY NEWS FOR SENTIMENT ANALYSIS")
    print("="*60)

    articles = get_articles_for_specific_dates("cryptocurrency", 30)
    
    if articles:
        print(f"Analyzing sentiment for {len(articles)} articles...")
        
        daily_scores = calculate_daily_faith_scores(articles)
        
        if daily_scores:
            df = save_daily_faith_scores(daily_scores)
            
            print(f"\nDaily Faith Scores Summary:")
            print(df.head(10))
            print("\n...")
            print(df.tail(10))
        else:
            print("No daily scores calculated")
    else:
        print("No articles found for analysis")