import os
import pandas as pd

def main():
    # Set style parameters for a modern dark theme matching the design system
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not installed. Installing matplotlib...")
        import subprocess
        subprocess.run(["pip", "install", "matplotlib"])
        import matplotlib.pyplot as plt
        import numpy as np

    # Configure matplotlib for dark theme
    plt.style.use('dark_background')
    
    # Custom color palette matching the Antigravity Premium theme
    bg_color = '#09090b'
    card_color = '#18181b'
    border_color = '#27272a'
    
    # Accent colors
    accent_violet = '#a855f7' # neon violet
    accent_cyan = '#06b6d4'   # electric cyan
    accent_amber = '#f59e0b'  # amber highlight
    accent_gray = '#71717a'
    
    # Update default parameters
    plt.rcParams['figure.facecolor'] = bg_color
    plt.rcParams['axes.facecolor'] = bg_color
    plt.rcParams['axes.edgecolor'] = border_color
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.color'] = '#27272a'
    plt.rcParams['grid.alpha'] = 0.5
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['text.color'] = '#f4f4f5'
    plt.rcParams['axes.labelcolor'] = '#a1a1aa'
    plt.rcParams['xtick.color'] = '#71717a'
    plt.rcParams['ytick.color'] = '#71717a'

    # Ensure resources directory exists
    os.makedirs('resources', exist_ok=True)

    # --- Chart 1: Scoring Component Weights ---
    print("Generating scoring weights chart...")
    components = [
        'Title & Career Fit',
        'Skill Trust',
        'Behavioral Signals',
        'Experience Fit',
        'Availability',
        'Education'
    ]
    weights = [35, 20, 20, 10, 10, 5]
    colors = [accent_violet, accent_cyan, accent_cyan, accent_amber, accent_amber, accent_gray]

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    bars = ax.barh(components, weights, color=colors, height=0.6, edgecolor='none', alpha=0.9)
    
    # Add value labels to the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width}%', 
                va='center', ha='left', color='#f4f4f5', fontweight='bold', fontsize=10)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(border_color)
    ax.spines['bottom'].set_color(border_color)
    
    ax.set_xlim(0, 45)
    ax.set_xlabel('Weight (%)', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_title('Redrob Candidate Ranking Engine: Signal Fusion Weights', fontsize=13, fontweight='bold', pad=20, color='#ffffff')
    ax.invert_yaxis()  # top-down
    
    plt.tight_layout()
    plt.savefig('resources/scoring_weights_chart.png', facecolor=bg_color, edgecolor='none', bbox_inches='tight')
    plt.close()
    print("Saved resources/scoring_weights_chart.png")

    # --- Chart 2: Top 100 Scores Distribution ---
    csv_path = 'submission.csv'
    if os.path.exists(csv_path):
        print("Generating score distribution chart from submission.csv...")
        df = pd.read_csv(csv_path)
        
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        # Plot line chart of scores vs rank
        ax.plot(df['rank'], df['score'], color=accent_cyan, linewidth=3, label='Candidate Score')
        ax.fill_between(df['rank'], df['score'], color=accent_cyan, alpha=0.15)

        # Highlight top 10
        ax.axvspan(1, 10, color=accent_violet, alpha=0.1, label='Top 10 Tier')
        
        # Add some annotations
        top_1_score = df.iloc[0]['score']
        top_10_score = df.iloc[9]['score']
        top_100_score = df.iloc[99]['score']
        
        ax.annotate(f'Rank 1: {top_1_score:.3f}', xy=(1, top_1_score), xytext=(15, top_1_score - 0.05),
                    arrowprops=dict(arrowstyle="->", color=accent_violet, connectionstyle="arc3,rad=-0.2"),
                    color=accent_violet, fontweight='bold')
        
        ax.annotate(f'Rank 100: {top_100_score:.3f}', xy=(100, top_100_score), xytext=(70, top_100_score + 0.08),
                    arrowprops=dict(arrowstyle="->", color=accent_gray, connectionstyle="arc3,rad=0.2"),
                    color=accent_gray, fontweight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(border_color)
        ax.spines['bottom'].set_color(border_color)

        ax.set_xlabel('Rank', fontsize=11, fontweight='bold', labelpad=10)
        ax.set_ylabel('Composite Score', fontsize=11, fontweight='bold', labelpad=10)
        ax.set_title('Score Distribution of Top 100 Ranked Candidates', fontsize=13, fontweight='bold', pad=20, color='#ffffff')
        ax.set_xlim(0, 105)
        ax.set_ylim(min(0.0, top_100_score - 0.1), max(1.0, top_1_score + 0.1))
        ax.legend(facecolor=card_color, edgecolor=border_color, loc='upper right')

        plt.tight_layout()
        plt.savefig('resources/score_distribution_chart.png', facecolor=bg_color, edgecolor='none', bbox_inches='tight')
        plt.close()
        print("Saved resources/score_distribution_chart.png")
    else:
        print("submission.csv not found, skipping distribution chart.")

if __name__ == '__main__':
    main()
