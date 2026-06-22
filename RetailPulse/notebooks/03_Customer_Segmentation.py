"""
RetailPulse: Week 1, Day 3 - Customer Segmentation with K-Means & DBSCAN
RFM-based clustering and business interpretation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import SEGMENTATION_N_CLUSTERS, RANDOM_SEED
from src.figure_utils import save_figure, save_plotly_figure, FIGURES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(f"📁 Figures will be saved to: {FIGURES_DIR}")

plt.rcParams['figure.figsize'] = (14, 6)

# ============================================================================
# SECTION 1: LOAD AND PREPARE DATA
# ============================================================================

def load_rfm_data():
    """Load RFM scores for clustering"""
    print("="*80)
    print("SECTION 1: LOAD RFM DATA FOR SEGMENTATION")
    print("="*80)
    
    rfm_path = Path(__file__).parent.parent / "data" / "rfm_scores.csv"
    rfm = pd.read_csv(rfm_path)
    
    print(f"\nRFM Data Shape: {rfm.shape}")
    print(f"Columns: {list(rfm.columns)}")
    print(f"\nRFM Statistics:")
    print(rfm[['Recency', 'Frequency', 'Monetary']].describe())
    
    return rfm


# ============================================================================
# SECTION 2: K-MEANS CLUSTERING
# ============================================================================

def find_optimal_clusters_kmeans(rfm, max_clusters=10):
    """
    Find optimal number of clusters using Elbow Method and Silhouette Score
    """
    print("\n" + "="*80)
    print("SECTION 2: K-MEANS CLUSTERING - OPTIMAL CLUSTER SELECTION")
    print("="*80)
    
    # Prepare data
    X = rfm[['Recency', 'Frequency', 'Monetary']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    inertias = []
    silhouette_scores = []
    davies_bouldin_scores = []
    K_range = range(2, max_clusters + 1)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))
        davies_bouldin_scores.append(davies_bouldin_score(X_scaled, kmeans.labels_))
    
    # Plot evaluation metrics
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    axes[0].plot(K_range, inertias, 'bo-')
    axes[0].set_xlabel('Number of Clusters (k)')
    axes[0].set_ylabel('Inertia')
    axes[0].set_title('Elbow Method')
    axes[0].grid(True)
    
    axes[1].plot(K_range, silhouette_scores, 'go-')
    axes[1].set_xlabel('Number of Clusters (k)')
    axes[1].set_ylabel('Silhouette Score')
    axes[1].set_title('Silhouette Score (Higher is Better)')
    axes[1].grid(True)
    
    axes[2].plot(K_range, davies_bouldin_scores, 'ro-')
    axes[2].set_xlabel('Number of Clusters (k)')
    axes[2].set_ylabel('Davies-Bouldin Index')
    axes[2].set_title('Davies-Bouldin Index (Lower is Better)')
    axes[2].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    print(f"\nOptimal Clusters Metrics:")
    for k, sil, db in zip(K_range, silhouette_scores, davies_bouldin_scores):
        print(f"  k={k}: Silhouette={sil:.4f}, Davies-Bouldin={db:.4f}")
    
    optimal_k = K_range[np.argmax(silhouette_scores)]
    print(f"\n✓ Recommended optimal clusters: {optimal_k}")
    
    return X_scaled, optimal_k


def perform_kmeans_clustering(rfm, X_scaled, n_clusters=SEGMENTATION_N_CLUSTERS):
    """
    Perform K-Means clustering
    """
    print(f"\n" + "="*80)
    print(f"PERFORMING K-MEANS CLUSTERING WITH k={n_clusters}")
    print("="*80)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=RANDOM_SEED, n_init=10)
    rfm['KMeans_Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Evaluate clustering
    silhouette = silhouette_score(X_scaled, rfm['KMeans_Cluster'])
    davies_bouldin = davies_bouldin_score(X_scaled, rfm['KMeans_Cluster'])
    calinski_harabasz = calinski_harabasz_score(X_scaled, rfm['KMeans_Cluster'])
    
    print(f"\nK-Means Evaluation Metrics:")
    print(f"  - Silhouette Score: {silhouette:.4f} (closer to 1 is better)")
    print(f"  - Davies-Bouldin Index: {davies_bouldin:.4f} (lower is better)")
    print(f"  - Calinski-Harabasz Index: {calinski_harabasz:.4f} (higher is better)")
    
    print(f"\nCluster Distribution:")
    print(rfm['KMeans_Cluster'].value_counts().sort_index())
    
    return rfm, kmeans


# ============================================================================
# SECTION 3: DBSCAN CLUSTERING
# ============================================================================

def perform_dbscan_clustering(rfm, X_scaled, eps=0.5, min_samples=5):
    """
    Perform DBSCAN clustering
    """
    print(f"\n" + "="*80)
    print(f"DBSCAN CLUSTERING (eps={eps}, min_samples={min_samples})")
    print("="*80)
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    rfm['DBSCAN_Cluster'] = dbscan.fit_predict(X_scaled)
    
    n_clusters = len(set(rfm['DBSCAN_Cluster'])) - (1 if -1 in rfm['DBSCAN_Cluster'] else 0)
    n_noise = list(rfm['DBSCAN_Cluster']).count(-1)
    
    print(f"\nDBSCAN Results:")
    print(f"  - Number of Clusters: {n_clusters}")
    print(f"  - Number of Noise Points: {n_noise}")
    print(f"  - Cluster Distribution:")
    print(rfm['DBSCAN_Cluster'].value_counts().sort_index())
    
    if n_clusters > 1:
        silhouette = silhouette_score(X_scaled, rfm['DBSCAN_Cluster'])
        print(f"  - Silhouette Score: {silhouette:.4f}")
    
    return rfm, dbscan


# ============================================================================
# SECTION 4: CLUSTER ANALYSIS & INTERPRETATION
# ============================================================================

def analyze_clusters(rfm, cluster_col='KMeans_Cluster'):
    """
    Analyze and interpret clusters
    """
    print("\n" + "="*80)
    print(f"CLUSTER ANALYSIS & BUSINESS INTERPRETATION ({cluster_col})")
    print("="*80)
    
    cluster_analysis = rfm.groupby(cluster_col)[['Recency', 'Frequency', 'Monetary']].agg({
        'Recency': ['mean', 'median'],
        'Frequency': ['mean', 'median'],
        'Monetary': ['mean', 'median']
    }).round(2)
    
    print(f"\n{cluster_col} Characteristics:")
    print(cluster_analysis)
    
    # Size and revenue contribution
    cluster_size = rfm[cluster_col].value_counts().sort_index()
    cluster_revenue = rfm.groupby(cluster_col)['Monetary'].sum().sort_values(ascending=False)
    
    print(f"\nCluster Size & Revenue Contribution:")
    for cluster in sorted(rfm[cluster_col].unique()):
        if cluster != -1:
            size = cluster_size[cluster]
            revenue = cluster_revenue[cluster]
            pct = (size / len(rfm)) * 100
            rev_pct = (revenue / rfm['Monetary'].sum()) * 100
            print(f"  Cluster {cluster}: {size} customers ({pct:.1f}%) | "
                  f"Revenue: ${revenue:.0f} ({rev_pct:.1f}%)")
    
    # Assign segment names
    segment_names = assign_segment_names(rfm, cluster_col)
    rfm[f'{cluster_col}_Segment'] = rfm[cluster_col].map(segment_names)
    
    print(f"\nSegment Names:")
    for cluster, name in segment_names.items():
        print(f"  Cluster {cluster}: {name}")
    
    return rfm, segment_names


def assign_segment_names(rfm, cluster_col='KMeans_Cluster'):
    """
    Assign business-meaningful names to segments
    """
    segment_data = rfm.groupby(cluster_col)[['Recency', 'Frequency', 'Monetary']].mean()
    
    segment_names = {}
    for cluster in segment_data.index:
        if cluster == -1:
            segment_names[cluster] = "Noise"
        else:
            rec = segment_data.loc[cluster, 'Recency']
            freq = segment_data.loc[cluster, 'Frequency']
            mon = segment_data.loc[cluster, 'Monetary']
            
            # Normalize to 0-1 scale for interpretation
            rec_norm = 1 - (rec / segment_data['Recency'].max())  # High = Recently active
            freq_norm = freq / segment_data['Frequency'].max()  # High = Frequent buyer
            mon_norm = mon / segment_data['Monetary'].max()  # High = High value
            
            if rec_norm > 0.7 and freq_norm > 0.7 and mon_norm > 0.7:
                name = "🌟 Champions"
            elif rec_norm > 0.6 and freq_norm > 0.6:
                name = "💎 Loyal Customers"
            elif rec_norm > 0.6 and freq_norm > 0.4:
                name = "🔄 At Risk"
            elif rec_norm < 0.3 and mon_norm > 0.5:
                name = "👑 VIPs (Lost)"
            else:
                name = f"Segment {cluster}"
            
            segment_names[cluster] = name
    
    return segment_names


# ============================================================================
# SECTION 5: VISUALIZATIONS
# ============================================================================

def visualize_clusters(rfm, X_scaled, cluster_col='KMeans_Cluster'):
    """
    Create comprehensive cluster visualizations
    """
    print(f"\nGenerating visualizations for {cluster_col}...")
    
    # 3D scatter plot
    fig = plt.figure(figsize=(16, 12))
    
    # 2D projections
    ax1 = plt.subplot(2, 3, 1)
    scatter = ax1.scatter(rfm['Recency'], rfm['Frequency'], 
                         c=rfm[cluster_col], cmap='viridis', s=50, alpha=0.6)
    ax1.set_xlabel('Recency (days)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Recency vs Frequency')
    plt.colorbar(scatter, ax=ax1)
    
    ax2 = plt.subplot(2, 3, 2)
    scatter = ax2.scatter(rfm['Frequency'], rfm['Monetary'], 
                         c=rfm[cluster_col], cmap='viridis', s=50, alpha=0.6)
    ax2.set_xlabel('Frequency')
    ax2.set_ylabel('Monetary Value')
    ax2.set_title('Frequency vs Monetary')
    plt.colorbar(scatter, ax=ax2)
    
    ax3 = plt.subplot(2, 3, 3)
    scatter = ax3.scatter(rfm['Recency'], rfm['Monetary'], 
                         c=rfm[cluster_col], cmap='viridis', s=50, alpha=0.6)
    ax3.set_xlabel('Recency (days)')
    ax3.set_ylabel('Monetary Value')
    ax3.set_title('Recency vs Monetary')
    plt.colorbar(scatter, ax=ax3)
    
    # Box plots
    ax4 = plt.subplot(2, 3, 4)
    rfm.boxplot(column='Recency', by=cluster_col, ax=ax4)
    ax4.set_title('Recency by Cluster')
    ax4.set_xlabel(cluster_col)
    
    ax5 = plt.subplot(2, 3, 5)
    rfm.boxplot(column='Frequency', by=cluster_col, ax=ax5)
    ax5.set_title('Frequency by Cluster')
    ax5.set_xlabel(cluster_col)
    
    ax6 = plt.subplot(2, 3, 6)
    rfm.boxplot(column='Monetary', by=cluster_col, ax=ax6)
    ax6.set_title('Monetary by Cluster')
    ax6.set_xlabel(cluster_col)
    
    plt.tight_layout()
    plt.show()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Load RFM data
    rfm = load_rfm_data()
    
    # Find optimal clusters
    X_scaled, optimal_k = find_optimal_clusters_kmeans(rfm, max_clusters=10)
    
    # Perform K-Means clustering
    rfm, kmeans = perform_kmeans_clustering(rfm, X_scaled, n_clusters=SEGMENTATION_N_CLUSTERS)
    
    # Perform DBSCAN clustering
    rfm, dbscan = perform_dbscan_clustering(rfm, X_scaled, eps=1.0, min_samples=5)
    
    # Analyze clusters
    rfm, kmeans_segments = analyze_clusters(rfm, 'KMeans_Cluster')
    rfm, dbscan_segments = analyze_clusters(rfm, 'DBSCAN_Cluster')
    
    # Visualize
    visualize_clusters(rfm, X_scaled, 'KMeans_Cluster')
    
    # Save results
    output_path = Path(__file__).parent.parent / "data" / "customer_segments.csv"
    rfm.to_csv(output_path, index=False)
    print(f"\n✓ Customer segments saved to {output_path}")
    
    print("\n" + "="*80)
    print("WEEK 1 CHECKPOINT: Customer Segmentation Complete")
    print("="*80)
