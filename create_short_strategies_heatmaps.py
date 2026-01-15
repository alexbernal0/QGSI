"""
Generate heatmaps with 3D surface plots for SHORT signal strategies
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')

def create_heatmap_with_3d(csv_file, strategy_name, output_file):
    """Create combined heatmap and 3D surface plot."""
    
    df = pd.read_csv(csv_file)
    
    # Get unique values
    atr_periods = sorted(df['ATRPeriod'].unique())
    
    if 'StopMultiplier' in df.columns and 'TargetMultiplier' in df.columns:
        # Asymmetric strategy
        stop_mults = sorted(df['StopMultiplier'].unique())
        target_mults = sorted(df['TargetMultiplier'].unique())
        
        # Create figure with 2 subplots
        fig = plt.figure(figsize=(20, 10))
        
        # Plot for each ATR period
        for idx, atr in enumerate(atr_periods):
            df_atr = df[df['ATRPeriod'] == atr]
            
            # Create pivot table
            pivot = df_atr.pivot_table(
                values='NetProfit',
                index='StopMultiplier',
                columns='TargetMultiplier',
                aggfunc='mean'
            )
            
            # Heatmap
            ax1 = plt.subplot(2, 4, idx + 1)
            im = ax1.imshow(pivot.values, cmap='RdYlGn', aspect='auto', origin='lower')
            ax1.set_xticks(range(len(target_mults)))
            ax1.set_yticks(range(len(stop_mults)))
            ax1.set_xticklabels([f'{x:.1f}×' for x in target_mults])
            ax1.set_yticklabels([f'{x:.1f}×' for x in stop_mults])
            ax1.set_xlabel('Target Multiplier', fontsize=10, fontweight='bold')
            ax1.set_ylabel('Stop Multiplier', fontsize=10, fontweight='bold')
            ax1.set_title(f'ATR({atr}) - Net Profit Heatmap', fontsize=11, fontweight='bold')
            
            # Add values
            for i in range(len(stop_mults)):
                for j in range(len(target_mults)):
                    value = pivot.values[i, j]
                    if not np.isnan(value):
                        color = 'white' if value < 0 else 'black'
                        ax1.text(j, i, f'${value/1000:.0f}K', 
                                ha='center', va='center', color=color, fontsize=8)
            
            plt.colorbar(im, ax=ax1, label='Net Profit ($)')
            
            # 3D Surface
            ax2 = plt.subplot(2, 4, idx + 5, projection='3d')
            X, Y = np.meshgrid(range(len(target_mults)), range(len(stop_mults)))
            Z = pivot.values
            
            surf = ax2.plot_surface(X, Y, Z, cmap='RdYlGn', alpha=0.8, 
                                   edgecolor='none', antialiased=True)
            ax2.set_xlabel('Target Mult', fontsize=9, fontweight='bold')
            ax2.set_ylabel('Stop Mult', fontsize=9, fontweight='bold')
            ax2.set_zlabel('Net Profit ($)', fontsize=9, fontweight='bold')
            ax2.set_title(f'ATR({atr}) - 3D Surface', fontsize=11, fontweight='bold')
            ax2.view_init(elev=25, azim=45)
            
    else:
        # Symmetric strategy
        multipliers = sorted(df['Multiplier'].unique())
        
        # Create pivot table
        pivot = df.pivot_table(
            values='NetProfit',
            index='ATRPeriod',
            columns='Multiplier',
            aggfunc='mean'
        )
        
        # Create figure
        fig = plt.figure(figsize=(20, 10))
        
        # Heatmap
        ax1 = plt.subplot(1, 2, 1)
        im = ax1.imshow(pivot.values, cmap='RdYlGn', aspect='auto', origin='lower')
        ax1.set_xticks(range(len(multipliers)))
        ax1.set_yticks(range(len(atr_periods)))
        ax1.set_xticklabels([f'{x:.1f}×' for x in multipliers])
        ax1.set_yticklabels([f'{x}' for x in atr_periods])
        ax1.set_xlabel('ATR Multiplier', fontsize=12, fontweight='bold')
        ax1.set_ylabel('ATR Period', fontsize=12, fontweight='bold')
        ax1.set_title(f'{strategy_name} - Net Profit Heatmap', fontsize=14, fontweight='bold')
        
        # Add values
        for i in range(len(atr_periods)):
            for j in range(len(multipliers)):
                value = pivot.values[i, j]
                color = 'white' if value < 0 else 'black'
                ax1.text(j, i, f'${value/1000:.0f}K', 
                        ha='center', va='center', color=color, fontsize=10)
        
        plt.colorbar(im, ax=ax1, label='Net Profit ($)')
        
        # 3D Surface
        ax2 = plt.subplot(1, 2, 2, projection='3d')
        X, Y = np.meshgrid(range(len(multipliers)), range(len(atr_periods)))
        Z = pivot.values
        
        surf = ax2.plot_surface(X, Y, Z, cmap='RdYlGn', alpha=0.8,
                               edgecolor='none', antialiased=True)
        ax2.set_xlabel('ATR Multiplier', fontsize=11, fontweight='bold')
        ax2.set_ylabel('ATR Period', fontsize=11, fontweight='bold')
        ax2.set_zlabel('Net Profit ($)', fontsize=11, fontweight='bold')
        ax2.set_title(f'{strategy_name} - 3D Surface', fontsize=14, fontweight='bold')
        ax2.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_file}")


# Generate visualizations
print("="*80)
print("GENERATING SHORT STRATEGY VISUALIZATIONS")
print("="*80)

# Strategy 1: Fixed ATR Symmetric
print("\n[1/2] Fixed ATR Symmetric SHORT...")
create_heatmap_with_3d(
    OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Performance.csv',
    'Fixed ATR Symmetric SHORT',
    OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Heatmap.png'
)

# Strategy 2: Fixed ATR Asymmetric
print("\n[2/2] Fixed ATR Asymmetric SHORT...")
create_heatmap_with_3d(
    OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Performance.csv',
    'Fixed ATR Asymmetric SHORT',
    OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Heatmap.png'
)

print("\n" + "="*80)
print("✓ All visualizations complete!")
print("="*80)
