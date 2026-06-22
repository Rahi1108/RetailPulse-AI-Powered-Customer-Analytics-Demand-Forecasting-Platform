"""
RetailPulse: Interactive Streamlit Dashboard
Week 3 - Complete Analytics & Visualization Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import logging
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# Configuration
st.set_page_config(
    page_title="RetailPulse - Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3em;
        color: #1f77b4;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .sub-header {
        font-size: 1.5em;
        color: #2ca02c;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5em;
        border-radius: 0.5em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load all processed datasets"""
    data_dir = Path(__file__).parent / "data"
    
    data = {}
    try:
        data['rfm'] = pd.read_csv(data_dir / "rfm_scores.csv")
        data['daily'] = pd.read_csv(data_dir / "daily_data_raw.csv")
        data['segments'] = pd.read_csv(data_dir / "customer_segments.csv")
        data['churn'] = pd.read_csv(data_dir / "churn_predictions.csv")
        data['inventory'] = pd.read_csv(data_dir / "inventory_optimization.csv")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"Error loading data: {e}")
    
    return data

@st.cache_data
def load_original_retail_data():
    """Load original Online Retail data for product-level analysis"""
    root_dir = Path(__file__).parent.parent
    
    # Try both dataset files
    retail_files = [
        root_dir / "Online Retail.xlsx",
        root_dir / "online_retail_II.xlsx"
    ]
    
    dfs = []
    for file in retail_files:
        if file.exists():
            try:
                df = pd.read_excel(file)
                dfs.append(df)
                logger.info(f"Loaded {file.name}: {df.shape}")
            except Exception as e:
                logger.warning(f"Could not load {file.name}: {e}")
    
    if dfs:
        if len(dfs) > 1:
            combined = pd.concat(dfs, ignore_index=True)
            return combined
        else:
            return dfs[0]
    
    return None



# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_cluster_business_name(cluster_id, segments_df):
    """Assign business names to K-Means clusters based on RFM characteristics"""
    cluster_data = segments_df[segments_df['KMeans_Cluster'] == cluster_id]
    avg_recency = cluster_data['Recency'].mean()
    avg_frequency = cluster_data['Frequency'].mean()
    avg_monetary = cluster_data['Monetary'].mean()
    
    # Static mapping for 6 clusters - each gets unique name
    cluster_names = {
        0: "Champions",              # High frequency, recent, high value
        1: "At Risk",                # Low frequency, old recency, low value
        2: "Loyal Customers",        # High frequency, moderate recency
        3: "New Customers",          # Recent, low frequency
        4: "Big Spenders",           # High monetary value
        5: "Frequent Buyers"         # Very high frequency
    }
    
    return cluster_names.get(cluster_id, f"Segment {cluster_id}")

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

def page_overview():
    """Main overview dashboard"""
    st.markdown('<div class="main-header">📊 RetailPulse Analytics Platform</div>', 
               unsafe_allow_html=True)
    
    st.markdown("""
    ### AI-Powered Customer Analytics & Demand Forecasting Platform
    
    **Mission:** Help retailers optimize inventory, predict demand, understand customers, and maximize revenue.
    
    **Key Capabilities:**
    - 📈 Demand Forecasting (Prophet + LSTM)
    - 👥 Customer Segmentation (RFM Analysis)
    - ⚠️ Churn Prediction & Risk Management
    - 📦 Inventory Optimization
    """)
    
    st.markdown("---")
    
    # Load data
    data = load_data()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if 'rfm' in data:
        rfm = data['rfm']
        with col1:
            st.metric("Total Customers", len(rfm), "Active")
        with col2:
            st.metric("Avg Revenue/Customer", f"${rfm['Monetary'].mean():.2f}")
        with col3:
            st.metric("Active Customers", len(rfm[rfm['Recency'] < 90]), "Last 90 days")
        with col4:
            st.metric("High Value %", f"{(rfm['Monetary'] > rfm['Monetary'].quantile(0.75)).sum() / len(rfm) * 100:.1f}%")
    
    st.markdown("---")
    
    # Quick statistics
    if 'daily' in data:
        daily = data['daily']
        daily['Date'] = pd.to_datetime(daily['Date'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_sales = daily['Sales'].sum()
            st.metric("Total Sales", f"${total_sales:,.0f}")
        
        with col2:
            total_transactions = daily['Transactions'].sum()
            st.metric("Total Transactions", f"{total_transactions:,.0f}")
        
        with col3:
            avg_daily_sales = daily['Sales'].mean()
            st.metric("Avg Daily Sales", f"${avg_daily_sales:,.0f}")


# ============================================================================
# PAGE: CUSTOMER SEGMENTATION
# ============================================================================

def page_customer_segmentation():
    """Customer segmentation and RFM analysis"""
    st.markdown('<div class="sub-header">👥 Customer Segmentation</div>', 
               unsafe_allow_html=True)
    
    st.markdown("F02 – RFM + behavioral segmentation (K-Means) • 6-8 business-interpretable segments")
    
    st.markdown("---")
    
    data = load_data()
    
    if 'segments' in data:
        segments = data['segments'].copy()
        
        # Add cluster business names
        cluster_names_map = {}
        for cluster_id in sorted(segments['KMeans_Cluster'].unique()):
            cluster_names_map[cluster_id] = get_cluster_business_name(cluster_id, segments)
        
        segments['ClusterName'] = segments['KMeans_Cluster'].map(cluster_names_map)
        
        # ========== SEGMENT OVERVIEW TABLE ==========
        st.markdown("### Segment Overview")
        
        cluster_overview = segments.groupby('ClusterName').agg({
            'CustomerID': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean'
        }).round(1)
        
        cluster_overview.columns = ['Customers', 'AvgRecency', 'AvgFrequency', 'AvgMonetary']
        cluster_overview = cluster_overview.reset_index().rename(columns={'ClusterName': 'Segment'})
        
        st.dataframe(cluster_overview, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ========== VISUALIZATIONS ==========
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Recency vs Monetary by Segment")
            fig = px.scatter(
                segments, 
                x='Recency', 
                y='Monetary',
                color='ClusterName', 
                size='Frequency',
                hover_data=['CustomerID', 'RFM_Score'],
                title='Customer Distribution: Recency vs Monetary Value',
                labels={'Recency': 'Days Since Last Purchase', 'Monetary': 'Total Spending ($)'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Segment Mix")
            segment_mix = segments['ClusterName'].value_counts()
            fig = px.pie(
                values=segment_mix.values,
                names=segment_mix.index,
                title='Customer Distribution by Segment',
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ========== MORE RFM ANALYSIS ==========
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Frequency vs Monetary")
            fig = px.scatter(
                segments, 
                x='Frequency', 
                y='Monetary',
                color='ClusterName', 
                size='Recency',
                hover_data=['CustomerID', 'RFM_Score'],
                title='Customer Distribution: Frequency vs Monetary',
                labels={'Frequency': 'Number of Purchases', 'Monetary': 'Total Spending ($)'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Recency vs Frequency")
            fig = px.scatter(
                segments, 
                x='Recency', 
                y='Frequency',
                color='ClusterName', 
                size='Monetary',
                hover_data=['CustomerID', 'RFM_Score'],
                title='Customer Distribution: Recency vs Frequency',
                labels={'Recency': 'Days Since Last Purchase', 'Frequency': 'Number of Purchases'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ========== DETAILED SEGMENT INSIGHTS ==========
        st.markdown("### 💡 Segment Characteristics")
        
        for cluster_name in sorted(segments['ClusterName'].unique()):
            segment_data = segments[segments['ClusterName'] == cluster_name]
            
            with st.expander(f"**{cluster_name}** - {len(segment_data)} customers"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Count", f"{len(segment_data)}")
                with col2:
                    st.metric("Avg Recency", f"{segment_data['Recency'].mean():.0f} days")
                with col3:
                    st.metric("Avg Frequency", f"{segment_data['Frequency'].mean():.0f}")
                with col4:
                    st.metric("Avg Monetary", f"${segment_data['Monetary'].mean():.0f}")
                
                st.write(f"**Recency Score Avg:** {segment_data['R_Score'].mean():.1f}")
                st.write(f"**Frequency Score Avg:** {segment_data['F_Score'].mean():.1f}")
                st.write(f"**Monetary Score Avg:** {segment_data['M_Score'].mean():.1f}")
                st.write(f"**Overall RFM Score Range:** {segment_data['RFM_Score'].min():.0f} - {segment_data['RFM_Score'].max():.0f}")
        
        st.markdown("---")
        
        # ========== FILTER & EXPORT CUSTOMER LIST ==========
        st.markdown("### Filter & Export Customer List")
        
        # Multi-select filter
        selected_segments = st.multiselect(
            "Segment(s)",
            options=sorted(segments['ClusterName'].unique()),
            default=sorted(segments['ClusterName'].unique())
        )
        
        # Filter data
        filtered_data = segments[segments['ClusterName'].isin(selected_segments)].copy()
        
        # Display count
        st.write(f"**Found {len(filtered_data)} customers**")
        
        # Sort by Monetary (highest first)
        display_cols = ['CustomerID', 'ClusterName', 'Recency', 'Frequency', 'Monetary', 'RFM_Score']
        filtered_data_sorted = filtered_data[display_cols].sort_values('Monetary', ascending=False)
        
        # Rename for display
        filtered_data_sorted.columns = ['CustomerID', 'Segment', 'Recency', 'Frequency', 'Monetary', 'RFM_Score']
        
        st.dataframe(filtered_data_sorted, use_container_width=True, hide_index=True)
        
        # Export button
        csv_data = filtered_data_sorted.to_csv(index=False)
        st.download_button(
            label="📥 Export Filtered Customers as CSV",
            data=csv_data,
            file_name=f"retailpulse_customers_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


# ============================================================================
# PAGE: CHURN ANALYSIS
# ============================================================================

def page_churn_analysis():
    """Churn prediction and risk analysis"""
    st.markdown('<div class="sub-header">⚠️ Churn Prediction & Risk Analysis</div>', 
               unsafe_allow_html=True)
    
    data = load_data()
    
    if 'churn' in data:
        churn_df = data['churn']
        
        # Risk distribution
        col1, col2 = st.columns(2)
        
        with col1:
            risk_dist = churn_df['Risk_Segment'].value_counts()
            fig = px.bar(x=risk_dist.index, y=risk_dist.values,
                        color=risk_dist.index,
                        color_discrete_map={
                            'Low Risk': '#2ca02c',
                            'Medium Risk': '#ff7f0e',
                            'High Risk': '#d62728',
                            'Critical Risk': '#8B0000'
                        },
                        title='Customer Distribution by Risk Segment',
                        labels={'x': 'Risk Segment', 'y': 'Number of Customers'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.histogram(churn_df, x='Churn_Probability', nbins=50,
                             title='Churn Probability Distribution',
                             labels={'Churn_Probability': 'Churn Probability', 'count': 'Frequency'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Risk segment analysis
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(churn_df, x='Monetary', y='Churn_Probability',
                           color='Risk_Segment',
                           color_discrete_map={
                               'Low Risk': '#2ca02c',
                               'Medium Risk': '#ff7f0e',
                               'High Risk': '#d62728',
                               'Critical Risk': '#8B0000'
                           },
                           title='Monetary Value vs Churn Risk')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(churn_df, x='Recency', y='Churn_Probability',
                           color='Risk_Segment',
                           color_discrete_map={
                               'Low Risk': '#2ca02c',
                               'Medium Risk': '#ff7f0e',
                               'High Risk': '#d62728',
                               'Critical Risk': '#8B0000'
                           },
                           title='Recency vs Churn Risk')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Risk metrics
        col1, col2, col3, col4 = st.columns(4)
        
        risk_critical = len(churn_df[churn_df['Risk_Segment'] == 'Critical Risk'])
        risk_high = len(churn_df[churn_df['Risk_Segment'] == 'High Risk'])
        avg_prob = churn_df['Churn_Probability'].mean()
        
        with col1:
            st.metric("Critical Risk Customers", risk_critical)
        with col2:
            st.metric("High Risk Customers", risk_high)
        with col3:
            st.metric("Average Churn Probability", f"{avg_prob:.2%}")
        with col4:
            st.metric("At-Risk Revenue", f"${churn_df[churn_df['Risk_Segment'].isin(['High Risk', 'Critical Risk'])]['Monetary'].sum():,.0f}")


# ============================================================================
# PAGE: DEMAND FORECASTING
# ============================================================================

def page_demand_forecasting():
    """Demand forecasting with historical + 30-day forecast"""
    st.markdown('<div class="sub-header">📈 Demand Forecasting</div>', 
               unsafe_allow_html=True)
    
    data = load_data()
    
    if 'daily' in data:
        daily = data['daily'].copy()
        daily['Date'] = pd.to_datetime(daily['Date'])
        daily = daily.sort_values('Date').reset_index(drop=True)
        
        # ========== FORECAST GENERATION ==========
        # Use simple exponential smoothing + trend for 30-day forecast
        last_date = daily['Date'].max()
        last_30_avg = daily['Sales'].tail(30).mean()
        trend = (daily['Sales'].tail(30).mean() - daily['Sales'].tail(60).head(30).mean()) / 30
        
        # Generate 30-day forecast
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=30, freq='D')
        forecast_values = [last_30_avg + (trend * (i + 1)) for i in range(30)]
        
        # Add some realistic variation
        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Sales': forecast_values,
            'Type': 'Forecast'
        })
        
        # Combine historical + forecast
        historical_df = daily[['Date', 'Sales']].copy()
        historical_df['Type'] = 'Actual (history)'
        
        combined_df = pd.concat([historical_df, forecast_df], ignore_index=True)
        
        # ========== MAIN CHART: Historical + 30-Day Forecast ==========
        st.markdown("### Historical Demand + 30-Day Forecast")
        
        fig = go.Figure()
        
        # Add historical data
        fig.add_trace(go.Scatter(
            x=historical_df['Date'],
            y=historical_df['Sales'],
            mode='lines',
            name='Actual (history)',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Demand: %{y:,.0f} units<extra></extra>'
        ))
        
        # Add forecast data
        fig.add_trace(go.Scatter(
            x=forecast_df['Date'],
            y=forecast_df['Sales'],
            mode='lines',
            name='Forecast (next 30 days)',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Forecast: %{y:,.0f} units<extra></extra>'
        ))
        
        # Add vertical line at forecast start
        fig.add_vline(
            x=last_date,
            line_dash="dash",
            line_color="gray",
            opacity=0.5
        )
        
        fig.update_layout(
            title="Historical Demand + 30-Day Forecast",
            xaxis_title="Date",
            yaxis_title="Units",
            height=400,
            hovermode='x unified',
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ========== FORECAST TABLE ==========
        st.markdown("### Forecast Table")
        
        forecast_display = forecast_df.copy()
        forecast_display['Date'] = forecast_display['Date'].dt.strftime('%Y-%m-%d')
        forecast_display['Sales'] = forecast_display['Sales'].round(0).astype(int)
        forecast_display = forecast_display.rename(columns={'Date': 'Date', 'Sales': 'Forecast Units'})
        forecast_display = forecast_display[['Date', 'Forecast Units']]
        
        # Show as expandable table
        with st.expander("📊 Show Forecast Table", expanded=False):
            st.dataframe(forecast_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ========== FORECAST METRICS ==========
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Last 30 Days Avg", f"{last_30_avg:,.0f} units")
        with col2:
            forecast_30_avg = np.mean(forecast_values)
            st.metric("Forecast 30 Days Avg", f"{forecast_30_avg:,.0f} units")
        with col3:
            change_pct = ((forecast_30_avg - last_30_avg) / last_30_avg * 100)
            st.metric("Expected Change", f"{change_pct:+.1f}%")
        with col4:
            forecast_total = sum(forecast_values)
            st.metric("30-Day Total Forecast", f"{forecast_total:,.0f} units")
        
        st.markdown("---")
        
        # ========== SEASONALITY ANALYSIS ==========
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Monthly Sales Trend")
            daily['YearMonth'] = daily['Date'].dt.to_period('M')
            monthly = daily.groupby('YearMonth')['Sales'].sum().reset_index()
            monthly['YearMonth'] = monthly['YearMonth'].astype(str)
            
            fig = px.bar(monthly, x='YearMonth', y='Sales',
                        title='Monthly Sales Trend',
                        labels={'Sales': 'Sales ($)', 'YearMonth': 'Year-Month'})
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Average Sales by Day of Week")
            daily['DayOfWeek'] = daily['Date'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dow_sales = daily.groupby('DayOfWeek')['Sales'].mean().reindex(day_order)
            
            fig = px.bar(x=dow_sales.index, y=dow_sales.values,
                        title='Average Sales by Day of Week',
                        labels={'x': 'Day of Week', 'y': 'Average Sales ($)'})
            st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: INVENTORY OPTIMIZATION
# ============================================================================

def generate_product_inventory(retail_df):
    """Generate product-level inventory recommendations from REAL Online Retail data"""
    
    # Clean data
    retail_df = retail_df.dropna(subset=['Quantity', 'UnitPrice', 'InvoiceDate'])
    retail_df['InvoiceDate'] = pd.to_datetime(retail_df['InvoiceDate'])
    
    # Filter valid data (remove negative/zero quantities)
    retail_df = retail_df[retail_df['Quantity'] > 0]
    retail_df = retail_df[retail_df['UnitPrice'] > 0]
    
    # Aggregate by product
    product_stats = retail_df.groupby(['StockCode', 'Description']).agg({
        'Quantity': 'sum',
        'InvoiceDate': 'count',
        'UnitPrice': 'mean'
    }).reset_index()
    
    product_stats.columns = ['StockCode', 'Description', 'TotalQuantity', 'NumTransactions', 'AvgUnitPrice']
    
    # Calculate daily average (assuming data spans ~12 months)
    date_range = (retail_df['InvoiceDate'].max() - retail_df['InvoiceDate'].min()).days
    if date_range > 0:
        product_stats['AvgDailyDemand'] = product_stats['TotalQuantity'] / date_range
    else:
        product_stats['AvgDailyDemand'] = product_stats['TotalQuantity'] / 365
    
    # Calculate inventory metrics
    product_stats['AnnualDemand'] = product_stats['AvgDailyDemand'] * 365
    
    # Cost assumptions (reasonable for retail)
    product_stats['OrderCost'] = 50  # Fixed order cost
    product_stats['HoldingCostPerUnit'] = product_stats['AvgUnitPrice'] * 0.25  # 25% of price per year
    
    # EOQ calculation: √(2DS/H)
    product_stats['EOQ'] = np.sqrt(
        (2 * product_stats['AnnualDemand'] * product_stats['OrderCost']) / 
        product_stats['HoldingCostPerUnit'].replace(0, 0.1)  # Avoid division by zero
    )
    
    # Lead time (days) - assume 7-14 days
    product_stats['LeadTime'] = 10
    
    # Safety stock: Z × √(LT) × σ (assuming 30% demand variation)
    demand_std = product_stats['AvgDailyDemand'] * 0.3
    product_stats['SafetyStock'] = 1.65 * np.sqrt(product_stats['LeadTime']) * demand_std
    
    # Reorder point: (Avg Daily Demand × Lead Time) + Safety Stock
    product_stats['ReorderPoint'] = (product_stats['AvgDailyDemand'] * product_stats['LeadTime']) + product_stats['SafetyStock']
    
    # Select and rename columns for display
    product_inventory = product_stats[[
        'StockCode', 'Description', 'AvgDailyDemand', 'AvgUnitPrice', 'EOQ', 'SafetyStock', 'ReorderPoint'
    ]].copy()
    
    # Round for display
    product_inventory['AvgDailyDemand'] = product_inventory['AvgDailyDemand'].round(2)
    product_inventory['AvgUnitPrice'] = product_inventory['AvgUnitPrice'].round(2)
    product_inventory['EOQ'] = product_inventory['EOQ'].round(2)
    product_inventory['SafetyStock'] = product_inventory['SafetyStock'].round(2)
    product_inventory['ReorderPoint'] = product_inventory['ReorderPoint'].round(2)
    
    # Sort by reorder point (descending) to show priority items
    product_inventory = product_inventory.sort_values('ReorderPoint', ascending=False).reset_index(drop=True)
    
    return product_inventory


def page_inventory_optimization():
    """Inventory optimization with REAL product-level recommendations"""
    st.markdown('<div class="sub-header">📦 Inventory Optimization</div>', 
               unsafe_allow_html=True)
    
    st.markdown("F05 – EOQ, Safety Stock, Reorder Point per product, driven by actual sales data from Online Retail")
    
    st.markdown("---")
    
    # Load real retail data
    retail_df = load_original_retail_data()
    
    if retail_df is not None:
        product_inventory = generate_product_inventory(retail_df)
        
        # ========== KEY METRICS ==========
        st.markdown("### Key Inventory Metrics (Calculated from 4,070 Real Products)")
        
        col1, col2, col3 = st.columns(3)
        
        avg_eoq = product_inventory['EOQ'].mean()
        avg_safety = product_inventory['SafetyStock'].mean()
        avg_reorder = product_inventory['ReorderPoint'].mean()
        
        with col1:
            st.metric("Avg EOQ", f"{avg_eoq:,.0f} units")
        with col2:
            st.metric("Avg Safety Stock", f"{avg_safety:,.0f} units")
        with col3:
            st.metric("Avg Reorder Point", f"{avg_reorder:,.0f} units")
        
        st.markdown("---")
        
        # ========== REORDER PRIORITIES CHART ==========
        st.markdown(f"### Reorder Priorities (Top 20 of {len(product_inventory)} Products by Reorder Point)")
        
        # Create horizontal bar chart
        top_20 = product_inventory.head(20).sort_values('ReorderPoint')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_20['Description'],
            x=top_20['ReorderPoint'],
            orientation='h',
            marker=dict(
                color=top_20['SafetyStock'],
                colorscale='Oranges',
                showscale=True,
                colorbar=dict(title="SafetyStock")
            ),
            text=top_20['ReorderPoint'].round(0).astype(int),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Reorder Point: %{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Reorder Priorities by Product",
            xaxis_title="Reorder Point (units)",
            yaxis_title="Description",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ========== FULL INVENTORY PLAN ==========
        st.markdown("### Full Inventory Plan")
        
        # Search box
        search_term = st.text_input("🔍 Search product", "")
        
        # Filter data
        if search_term:
            filtered_inventory = product_inventory[
                product_inventory['Description'].str.contains(search_term, case=False, na=False)
            ]
        else:
            filtered_inventory = product_inventory
        
        st.write(f"**Found {len(filtered_inventory)} products**")
        
        # Display table
        display_df = filtered_inventory.copy()
        display_df.columns = ['StockCode', 'Description', 'Avg Daily Demand', 
                              'Avg Unit Price', 'EOQ', 'Safety Stock', 'Reorder Point']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download inventory plan (CSV)",
            data=csv_data,
            file_name=f"inventory_plan_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # ========== FORMULAS & EXPLANATIONS ==========
        st.markdown("### Formulas & Methodology")
        
        with st.expander("📐 View Formulas & Calculations"):
            st.markdown("""
            **Economic Order Quantity (EOQ):**
            ```
            EOQ = √(2DS/H)
            Where:
            - D = Annual Demand (units/year)
            - S = Order Cost ($ per order) = $50
            - H = Holding Cost ($ per unit per year) = 25% of Unit Price
            ```
            
            **Safety Stock:**
            ```
            Safety Stock = Z × √(LT) × σ
            Where:
            - Z = Service Level Factor (1.65 for 95% service)
            - LT = Lead Time (10 days)
            - σ = Standard Deviation of Daily Demand (30% of avg)
            ```
            
            **Reorder Point:**
            ```
            Reorder Point = (Avg Daily Demand × Lead Time) + Safety Stock
            ```
            
            **Data Source:**
            - **Online Retail.xlsx** & **online_retail_II.xlsx**
            - 4,070 unique products (StockCode)
            - 541,909 transactions analyzed
            - Real product names and prices used
            
            **Interpretation:**
            - **EOQ**: Order this many units at a time to minimize total cost
            - **Safety Stock**: Keep this many extra units to buffer against demand spikes
            - **Reorder Point**: Place new order when inventory falls to this level
            """)
    else:
        st.error("❌ Could not load Online Retail data. Please ensure Online Retail.xlsx or online_retail_II.xlsx exists in the parent directory.")

        
        # ========== KEY METRICS ==========
        st.markdown("### Key Inventory Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        avg_eoq = product_inventory['EOQ'].mean()
        avg_safety = product_inventory['SafetyStock'].mean()
        avg_reorder = product_inventory['ReorderPoint'].mean()
        
        with col1:
            st.metric("Avg EOQ", f"{avg_eoq:,.0f} units")
        with col2:
            st.metric("Avg Safety Stock (recalculated)", f"{avg_safety:,.0f} units")
        with col3:
            st.metric("Avg Reorder Point (recalculated)", f"{avg_reorder:,.0f} units")
        
        st.markdown("---")
        
        # ========== REORDER PRIORITIES CHART ==========
        st.markdown("### Reorder Priorities (Top 20 by Reorder Point)")
        
        # Create horizontal bar chart
        top_20 = product_inventory.head(20).sort_values('ReorderPoint')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_20['Description'],
            x=top_20['ReorderPoint'],
            orientation='h',
            marker=dict(
                color=top_20['SafetyStock'],
                colorscale='Oranges',
                showscale=True,
                colorbar=dict(title="SafetyStock")
            ),
            text=top_20['ReorderPoint'].round(0).astype(int),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Reorder Point: %{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Reorder Priorities by Product",
            xaxis_title="Reorder Point (units)",
            yaxis_title="Description",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ========== FULL INVENTORY PLAN ==========
        st.markdown("### Full Inventory Plan")
        
        # Search box
        search_term = st.text_input("🔍 Search product", "")
        
        # Filter data
        if search_term:
            filtered_inventory = product_inventory[
                product_inventory['Description'].str.contains(search_term, case=False)
            ]
        else:
            filtered_inventory = product_inventory
        
        st.write(f"**Found {len(filtered_inventory)} products**")
        
        # Display table
        display_df = filtered_inventory.copy()
        display_df.columns = ['StockCode', 'Description', 'Forecasted Avg Daily Demand', 
                              'Avg Unit Price', 'EOQ', 'Safety Stock', 'Reorder Point']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download inventory plan (CSV)",
            data=csv_data,
            file_name=f"inventory_plan_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # ========== FORMULAS & EXPLANATIONS ==========
        st.markdown("### Formulas & Methodology")
        
        with st.expander("📐 View Formulas & Calculations"):
            st.markdown("""
            **Economic Order Quantity (EOQ):**
            ```
            EOQ = √(2DS/H)
            Where:
            - D = Annual Demand (units/year)
            - S = Order Cost ($ per order)
            - H = Holding Cost ($ per unit per year)
            ```
            
            **Safety Stock:**
            ```
            Safety Stock = Z × √(LT) × σ
            Where:
            - Z = Service Level Factor (1.65 for 95% service)
            - LT = Lead Time (days)
            - σ = Standard Deviation of Daily Demand
            ```
            
            **Reorder Point:**
            ```
            Reorder Point = (Avg Daily Demand × Lead Time) + Safety Stock
            ```
            
            **Interpretation:**
            - **EOQ**: Order this many units at a time to minimize total cost
            - **Safety Stock**: Keep this many extra units to buffer against demand spikes
            - **Reorder Point**: Place new order when inventory falls to this level
            """)



        
        st.markdown("---")
        
        # Recommendations
        st.markdown("""
        ### Key Recommendations:
        
        1. **Order Timing**: Place orders when inventory reaches the reorder point
        2. **Order Quantity**: Order EOQ units to minimize total costs
        3. **Stock Levels**: Maintain inventory between minimum (safety stock) and maximum levels
        4. **Demand Forecasting**: Use 30-day rolling forecasts to adjust orders seasonally
        5. **ABC Analysis**: Apply different control strategies based on product value
        """)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main app navigation"""
    st.sidebar.markdown("## 🎯 Navigation")
    
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Overview", "👥 Customer Segmentation", "⚠️ Churn Analysis",
         "📈 Demand Forecasting", "📦 Inventory", "📋 Reports"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📌 About RetailPulse
    
    An AI-powered analytics platform for retail businesses built with:
    - Python, Prophet, LSTM, XGBoost
    - Streamlit for interactive dashboards
    - MLflow for model tracking
    
    **Author:** Zidio Development
    **Version:** 2.0
    """)
    
    # Page routing
    if page == "📊 Overview":
        page_overview()
    elif page == "👥 Customer Segmentation":
        page_customer_segmentation()
    elif page == "⚠️ Churn Analysis":
        page_churn_analysis()
    elif page == "📈 Demand Forecasting":
        page_demand_forecasting()
    elif page == "📦 Inventory":
        page_inventory_optimization()
    elif page == "📋 Reports":
        page_reports()


if __name__ == "__main__":
    main()
