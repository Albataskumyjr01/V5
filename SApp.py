import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import datetime
import math

# =============================================================================
# CONFIGURATION AND BRANDING
# =============================================================================
st.set_page_config(
    page_title="Annur Tech Solar Planner", 
    layout="wide", 
    page_icon="☀️",
    initial_sidebar_state="expanded"
)

# Company branding
COMPANY = "ANNUR TECH SOLAR SOLUTIONS"
MOTTO = "Illuminating Nigeria's Future"
ADDRESS = "No 6 Kolo Drive, Behind Zuma Barrack, Tafa LGA, Niger State, Nigeria"
PHONE = "+234 905 169 3000"
EMAIL = "albataskumyjr@gmail.com"
WEBSITE = "www.annurtech.ng"

# Nigerian-specific component database (updated with realistic values)
NIGERIAN_SOLAR_PANELS = {
    "Jinko Tiger 350W": {"price": 85000, "vmp": 35.5, "isc": 9.8, "voc": 42.5},
    "Canadian Solar 400W": {"price": 105000, "vmp": 37.2, "isc": 10.9, "voc": 45.5},
    "Trina Solar 450W": {"price": 125000, "vmp": 39.8, "isc": 11.3, "voc": 48.2},
}

NIGERIAN_BATTERIES = {
    "Trojan T-105 (225Ah)": {"price": 65000, "capacity": 225, "voltage": 6, "type": "Lead Acid"},
    "Pylontech US2000 (200Ah)": {"price": 280000, "capacity": 200, "voltage": 48, "type": "Li-ion"},
    "Vision 6FM200D (200Ah)": {"price": 75000, "capacity": 200, "voltage": 6, "type": "Lead Acid"},
}

NIGERIAN_INVERTERS = {
    "Growatt 3000W 24V": {"price": 185000, "power": 3000, "voltage": 24, "type": "Hybrid"},
    "Victron 5000W 48V": {"price": 450000, "power": 5000, "voltage": 48, "type": "Hybrid"},
    "SMA Sunny Boy 5000W": {"price": 520000, "power": 5000, "voltage": 48, "type": "Grid-Tie"},
}

NIGERIAN_CHARGE_CONTROLLERS = {
    "EPever 40A MPPT": {"price": 45000, "current": 40, "voltage": 150, "type": "MPPT"},
    "Victron 100/50 MPPT": {"price": 85000, "current": 50, "voltage": 100, "type": "MPPT"},
    "EPever 60A MPPT": {"price": 65000, "current": 60, "voltage": 150, "type": "MPPT"},
}

# Common Nigerian appliances with typical wattages and usage patterns
NIGERIAN_APPLIANCES = {
    "Ceiling Fan": {"watt": 75, "hours": 8.0},
    "Standing Fan": {"watt": 55, "hours": 6.0},
    "TV (32-inch LED)": {"watt": 50, "hours": 5.0},
    "TV (42-inch LED)": {"watt": 80, "hours": 5.0},
    "Refrigerator (Medium)": {"watt": 150, "hours": 8.0},
    "Deep Freezer": {"watt": 200, "hours": 10.0},
    "Air Conditioner (1HP)": {"watt": 750, "hours": 6.0},
    "Air Conditioner (1.5HP)": {"watt": 1100, "hours": 6.0},
    "Water Pump (1HP)": {"watt": 750, "hours": 2.0},
    "Lighting (LED Bulb)": {"watt": 10, "hours": 8.0},
    "Computer Desktop": {"watt": 200, "hours": 4.0},
    "Laptop": {"watt": 65, "hours": 5.0},
    "Decoder": {"watt": 25, "hours": 6.0},
    "Home Theatre": {"watt": 100, "hours": 3.0},
    "Washing Machine": {"watt": 500, "hours": 2.0},
    "Electric Iron": {"watt": 1000, "hours": 1.0},
    "Microwave Oven": {"watt": 1000, "hours": 0.5},
    "Electric Kettle": {"watt": 1500, "hours": 0.5},
}

# =============================================================================
# CSS STYLING
# =============================================================================
st.markdown(f"""
<style>
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    .stApp {{
        background-color: #f8f9fa;
    }}
    .green-header {{
        background-color: #006400;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
    }}
    .nigerian-flag {{
        background: linear-gradient(90deg, #008751 33%, white 33%, white 66%, #008751 66%);
        color: white;
        padding: 10px;
        text-align: center;
        border-radius: 5px;
        margin-bottom: 20px;
    }}
    .input-label {{
        font-weight: bold;
        margin-bottom: 8px;
        display: block;
        color: #006400;
    }}
    .help-text {{
        font-size: 12px;
        color: #666;
        font-style: italic;
        margin-top: 4px;
    }}
    .section-box {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border-left: 5px solid #006400;
    }}
    .metric-card {{
        background-color: #f0fff0;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #006400;
        margin-bottom: 15px;
    }}
    .stButton>button {{
        background-color: #006400;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: #004d00;
        color: white;
    }}
    .footer {{
        text-align: center;
        color: #666;
        font-size: 12px;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #ddd;
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# INITIALIZATION
# =============================================================================
# Initialize session state
if "load_data" not in st.session_state:
    st.session_state.load_data = []
if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None
if "calculations" not in st.session_state:
    st.session_state.calculations = {}

# =============================================================================
# HEADER SECTION
# =============================================================================
st.markdown(f'<div class="nigerian-flag"><h1>⚡ {COMPANY}</h1></div>', unsafe_allow_html=True)
st.markdown(f'<h3 style="text-align: center; color: #006400;">{MOTTO}</h3>', unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - CLIENT INFORMATION
# =============================================================================
with st.sidebar:
    st.markdown(f'<div class="green-header"><h3>👤 Client Information</h3></div>', unsafe_allow_html=True)
    
    with st.container():
        client_name = st.text_input("**Full Name**", placeholder="Enter client's full name", key="client_name")
        client_address = st.text_area("**Address**", placeholder="Enter complete address", key="client_address")
        client_phone = st.text_input("**Phone Number**", placeholder="e.g., 08012345678", key="client_phone")
        client_email = st.text_input("**Email Address**", placeholder="client@example.com", key="client_email")
        project_location = st.selectbox("**Project Location**", 
                                       ["Abuja", "Lagos", "Kano", "Port Harcourt", "Kaduna", "Other"], 
                                       key="project_location")
        
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        {COMPANY}<br>
        {PHONE} | {EMAIL}<br>
        {ADDRESS}
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN CONTENT - TABBED INTERFACE
# =============================================================================
tab1, tab2, tab3, tab4 = st.tabs(["🔋 Load Audit", "⚡ System Sizing", "💰 Financials", "📋 Report"])

# =============================================================================
# TAB 1: LOAD AUDIT
# =============================================================================
with tab1:
    st.markdown(f'<div class="green-header"><h3>🔋 Load Audit & Energy Assessment</h3></div>', unsafe_allow_html=True)
    
    with st.expander("💡 Quick Add Common Appliances", expanded=True):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            selected_appliance = st.selectbox("Select Appliance", list(NIGERIAN_APPLIANCES.keys()), key="appliance_select")
            appliance_info = NIGERIAN_APPLIANCES[selected_appliance]
            
        with col2:
            appliance_wattage = st.number_input("Wattage (W)", 
                                              value=appliance_info["watt"],
                                              min_value=1, 
                                              max_value=5000, 
                                              key="appliance_wattage")
            
        with col3:
            appliance_quantity = st.number_input("Quantity", 
                                               value=1,
                                               min_value=1, 
                                               max_value=100, 
                                               key="appliance_quantity")
            
        with col4:
            appliance_hours = st.number_input("Hours/Day", 
                                            value=float(appliance_info["hours"]),  # Fixed: Convert to float
                                            min_value=0.0, 
                                            max_value=24.0, 
                                            step=0.5,
                                            key="appliance_hours")
            
        add_appliance = st.button("➕ Add to Load List", use_container_width=True, key="add_appliance_btn")

    with st.expander("⚙️ Custom Appliance Entry", expanded=False):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            custom_appliance = st.text_input("Appliance Name", placeholder="e.g., Water Dispenser", key="custom_name")
            
        with col2:
            custom_watt = st.number_input("Wattage (W)", 
                                        value=100,
                                        min_value=1, 
                                        max_value=5000, 
                                        key="custom_watt_input")
            
        with col3:
            custom_quantity = st.number_input("Quantity", 
                                            value=1,
                                            min_value=1, 
                                            max_value=100, 
                                            key="custom_quantity_input")
            
        with col4:
            custom_hours = st.number_input("Hours/Day", 
                                         value=5.0,
                                         min_value=0.0, 
                                         max_value=24.0, 
                                         step=0.5,
                                         key="custom_hours_input")
            
        add_custom = st.button("➕ Add Custom Appliance", use_container_width=True, key="add_custom_btn")

    # Add appliances to load list
    if add_appliance and selected_appliance:
        total_watt = appliance_wattage * appliance_quantity
        daily_wh = total_watt * appliance_hours
        st.session_state.load_data.append({
            "appliance": selected_appliance,
            "watt": appliance_wattage,
            "quantity": appliance_quantity,
            "total_watt": total_watt,
            "hours": appliance_hours,
            "wh": daily_wh
        })
        st.success(f"Added {appliance_quantity} × {selected_appliance}")

    if add_custom and custom_appliance:
        total_watt = custom_watt * custom_quantity
        daily_wh = total_watt * custom_hours
        st.session_state.load_data.append({
            "appliance": custom_appliance,
            "watt": custom_watt,
            "quantity": custom_quantity,
            "total_watt": total_watt,
            "hours": custom_hours,
            "wh": daily_wh
        })
        st.success(f"Added {custom_quantity} × {custom_appliance}")

    # Display load summary
    if st.session_state.load_data:
        st.markdown("---")
        st.subheader("📊 Load Summary")
        
        total_wh = sum(item["wh"] for item in st.session_state.load_data)
        total_watt = sum(item["total_watt"] for item in st.session_state.load_data)
        
        # Store for use in other tabs
        st.session_state.calculations["total_wh"] = total_wh
        st.session_state.calculations["total_watt"] = total_watt
        
        df = pd.DataFrame(st.session_state.load_data)
        
        # Energy consumption charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(df, values='wh', names='appliance', 
                            title='Energy Consumption by Appliance',
                            color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(df, x='appliance', y='wh', 
                            title='Daily Energy Consumption (Wh)',
                            color_discrete_sequence=['#006400'])
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Display data table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Key metrics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-card"><h4>Total Power Demand</h4><h3>{total_watt} W</h3></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h4>Daily Energy Consumption</h4><h3>{total_wh} Wh</h3></div>', unsafe_allow_html=True)
        
        # Clear button
        if st.button("🗑️ Clear All Items", use_container_width=True, key="clear_items_btn"):
            st.session_state.load_data = []
            st.session_state.pdf_data = None
            st.session_state.calculations = {}
            st.rerun()
    else:
        st.info("👆 Add appliances to your load list to see the summary here.")

# =============================================================================
# TAB 2: SYSTEM SIZING
# =============================================================================
with tab2:
    st.markdown(f'<div class="green-header"><h3>⚡ System Sizing & Component Selection</h3></div>', unsafe_allow_html=True)
    
    if not st.session_state.load_data:
        st.warning("Please add appliances in the Load Audit tab first.")
    else:
        total_wh = st.session_state.calculations.get("total_wh", 0)
        total_watt = st.session_state.calculations.get("total_watt", 0)
        
        with st.expander("🔋 Battery Bank Sizing", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                backup_time = st.slider("Backup Time Required (hours)", 
                                       min_value=1, 
                                       max_value=24, 
                                       value=5, 
                                       key="backup_time",
                                       help="How many hours of backup power you need during outages")
                
                battery_voltage = st.selectbox("System Voltage", 
                                              [12, 24, 48], 
                                              index=1, 
                                              key="battery_voltage",
                                              help="Standard system voltage for your installation")
                
                dod_limit = st.slider("Depth of Discharge (%)", 
                                     min_value=50, 
                                     max_value=100, 
                                     value=80, 
                                     key="dod_limit",
                                     help="How much of the battery capacity you can use (lower is better for battery life)")
                
            with col2:
                temperature_factor = st.slider("Temperature Derating Factor (%)", 
                                             min_value=80, 
                                             max_value=100, 
                                             value=90, 
                                             key="temp_factor",
                                             help="Reduction in battery capacity due to high temperatures")
                
                battery_type = st.selectbox("Battery Technology", 
                                          list(NIGERIAN_BATTERIES.keys()), 
                                          key="battery_type",
                                          help="Choose the type of battery for your system")
                
                battery_info = NIGERIAN_BATTERIES[battery_type]
                
            # Battery calculation
            battery_capacity_ah = (total_wh * backup_time) / (battery_voltage * (dod_limit/100) * (temperature_factor/100))
            num_batteries = battery_capacity_ah / battery_info["capacity"]
            
            # Store for use in other tabs
            st.session_state.calculations["battery_capacity_ah"] = battery_capacity_ah
            st.session_state.calculations["num_batteries"] = num_batteries
            st.session_state.calculations["battery_info"] = battery_info
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="metric-card"><h4>Required Battery Capacity</h4><h3>{battery_capacity_ah:.0f} Ah</h3></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><h4>Number of Batteries Needed</h4><h3>{num_batteries:.1f}</h3></div>', unsafe_allow_html=True)
        
        with st.expander("☀️ Solar Panel Sizing", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                sun_hours = st.slider("Sun Hours Per Day (Nigeria average)", 
                                     min_value=3.0, 
                                     max_value=8.0, 
                                     value=5.0, 
                                     step=0.5,
                                     key="sun_hours",
                                     help="Average daily peak sun hours at your location")
                
                system_efficiency = st.slider("System Efficiency (%)", 
                                            min_value=50, 
                                            max_value=95, 
                                            value=75, 
                                            key="system_eff",
                                            help="Overall efficiency of the solar system")
                
            with col2:
                panel_type = st.selectbox("Solar Panel Type", 
                                        list(NIGERIAN_SOLAR_PANELS.keys()), 
                                        key="panel_type",
                                        help="Choose the type of solar panel for your system")
                
                panel_info = NIGERIAN_SOLAR_PANELS[panel_type]
            
            # Solar calculation
            required_solar = (total_wh * 1.2) / (sun_hours * (system_efficiency/100))  # 20% margin for losses
            num_panels = required_solar / panel_info["vmp"] * (battery_voltage/panel_info["vmp"])
            
            # Charge controller calculation
            controller_current = (required_solar * 1.25) / battery_voltage  # 25% safety margin
            
            # Store for use in other tabs
            st.session_state.calculations["required_solar"] = required_solar
            st.session_state.calculations["num_panels"] = num_panels
            st.session_state.calculations["panel_info"] = panel_info
            st.session_state.calculations["controller_current"] = controller_current
            
            # Display results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-card"><h4>Required Solar Capacity</h4><h3>{required_solar:.0f} W</h3></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><h4>Number of Panels Needed</h4><h3>{num_panels:.1f}</h3></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-card"><h4>Charge Controller Size</h4><h3>{controller_current:.0f} A</h3></div>', unsafe_allow_html=True)
        
        with st.expander("🔌 Inverter Selection", expanded=True):
            # Inverter selection
            inverter_size = max(total_watt * 1.3, 1000)  # 30% safety margin, minimum 1000W
            
            # Find appropriate inverter
            suitable_inverters = {k: v for k, v in NIGERIAN_INVERTERS.items() 
                                 if v['power'] >= inverter_size and v['voltage'] == battery_voltage}
            
            if suitable_inverters:
                selected_inverter = list(suitable_inverters.keys())[0]
                inverter_info = suitable_inverters[selected_inverter]
            else:
                # Fallback to smallest compatible inverter
                compatible_inverters = {k: v for k, v in NIGERIAN_INVERTERS.items() 
                                       if v['voltage'] == battery_voltage}
                if compatible_inverters:
                    selected_inverter = list(compatible_inverters.keys())[0]
                    inverter_info = compatible_inverters[selected_inverter]
                else:
                    selected_inverter = "No suitable inverter found"
                    inverter_info = {"price": 0, "power": 0}
            
            # Store for use in other tabs
            st.session_state.calculations["inverter_size"] = inverter_size
            st.session_state.calculations["selected_inverter"] = selected_inverter
            st.session_state.calculations["inverter_info"] = inverter_info
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="metric-card"><h4>Recommended Inverter Size</h4><h3>{inverter_size:.0f} W</h3></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><h4>Selected Inverter</h4><h3>{selected_inverter}</h3></div>', unsafe_allow_html=True)

# =============================================================================
# TAB 3: FINANCIAL ANALYSIS
# =============================================================================
with tab3:
    st.markdown(f'<div class="green-header"><h3>💰 Financial Analysis & Cost Estimation</h3></div>', unsafe_allow_html=True)
    
    if not st.session_state.load_data:
        st.warning("Please add appliances in the Load Audit tab first.")
    else:
        # Get calculated values
        total_wh = st.session_state.calculations.get("total_wh", 0)
        battery_info = st.session_state.calculations.get("battery_info", {})
        num_batteries = st.session_state.calculations.get("num_batteries", 0)
        panel_info = st.session_state.calculations.get("panel_info", {})
        num_panels = st.session_state.calculations.get("num_panels", 0)
        inverter_info = st.session_state.calculations.get("inverter_info", {})
        controller_current = st.session_state.calculations.get("controller_current", 0)
        
        # Calculate costs
        battery_cost = math.ceil(num_batteries) * battery_info.get("price", 0)
        solar_cost = math.ceil(num_panels) * panel_info.get("price", 0)
        inverter_cost = inverter_info.get("price", 0)
        
        # Find suitable charge controller
        suitable_controllers = {k: v for k, v in NIGERIAN_CHARGE_CONTROLLERS.items() 
                              if v['current'] >= controller_current and v['voltage'] >= panel_info.get("voc", 0) * math.ceil(num_panels)}
        
        if suitable_controllers:
            selected_controller = list(suitable_controllers.keys())[0]
            controller_info = suitable_controllers[selected_controller]
            controller_cost = controller_info.get("price", 0)
        else:
            selected_controller = "No suitable controller found"
            controller_cost = 0
        
        # Other costs
        installation_cost = max(150000, (battery_cost + solar_cost + inverter_cost + controller_cost) * 0.2)  # 20% of equipment cost or 150k min
        wiring_cost = max(50000, (battery_cost + solar_cost + inverter_cost + controller_cost) * 0.1)  # 10% of equipment cost or 50k min
        
        total_cost = battery_cost + solar_cost + inverter_cost + controller_cost + installation_cost + wiring_cost
        
        # Store for use in PDF
        st.session_state.calculations["battery_cost"] = battery_cost
        st.session_state.calculations["solar_cost"] = solar_cost
        st.session_state.calculations["inverter_cost"] = inverter_cost
        st.session_state.calculations["controller_cost"] = controller_cost
        st.session_state.calculations["installation_cost"] = installation_cost
        st.session_state.calculations["wiring_cost"] = wiring_cost
        st.session_state.calculations["total_cost"] = total_cost
        st.session_state.calculations["selected_controller"] = selected_controller
        
        # Display cost breakdown
        st.subheader("💰 Cost Breakdown")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><h4>Battery Cost</h4><h3>₦{battery_cost:,.0f}</h3></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h4>Solar Panel Cost</h4><h3>₦{solar_cost:,.0f}</h3></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h4>Inverter Cost</h4><h3>₦{inverter_cost:,.0f}</h3></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><h4>Controller Cost</h4><h3>₦{controller_cost:,.0f}</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-card"><h4>Installation Cost</h4><h3>₦{installation_cost:,.0f}</h3></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h4>Wiring & Accessories</h4><h3>₦{wiring_cost:,.0f}</h3></div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="metric-card"><h4>Total System Cost</h4><h2>₦{total_cost:,.0f}</h2></div>', unsafe_allow_html=True)
        
        # Financial Analysis
        st.subheader("💵 Financial Analysis")
        
        current_electricity_rate = st.number_input("Current Electricity Cost (₦/kWh)", 
                                                  min_value=25, 
                                                  max_value=100, 
                                                  value=50, 
                                                  key="elec_rate",
                                                  help="Your current cost per kWh from the grid")
        
        monthly_energy_kwh = total_wh / 1000
        monthly_savings = monthly_energy_kwh * 30 * current_electricity_rate
        annual_savings = monthly_savings * 12
        
        system_lifespan = st.slider("System Lifespan (years)", 
                                   min_value=5, 
                                   max_value=25, 
                                   value=10, 
                                   key="system_lifespan")
        
        lifetime_savings = annual_savings * system_lifespan
        payback_period = total_cost / annual_savings if annual_savings > 0 else 0
        roi = ((lifetime_savings - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-card"><h4>Monthly Energy Consumption</h4><h3>{monthly_energy_kwh:.1f} kWh</h3></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><h4>Monthly Savings</h4><h3>₦{monthly_savings:,.0f}</h3></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h4>Annual Savings</h4><h3>₦{annual_savings:,.0f}</h3></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><h4>Payback Period</h4><h3>{payback_period:.1f} years</h3></div>', unsafe_allow_html=True)

# =============================================================================
# TAB 4: REPORT GENERATION
# =============================================================================
with tab4:
    st.markdown(f'<div class="green-header"><h3>📋 Professional Report</h3></div>', unsafe_allow_html=True)
    
    if not client_name or not st.session_state.load_data:
        st.warning("Please fill in client information and add at least one appliance first.")
    else:
        # PDF Generation Function
        def create_professional_pdf():
            buffer = BytesIO()
            
            # Get all calculated values
            total_wh = st.session_state.calculations.get("total_wh", 0)
            total_watt = st.session_state.calculations.get("total_watt", 0)
            battery_capacity_ah = st.session_state.calculations.get("battery_capacity_ah", 0)
            num_batteries = st.session_state.calculations.get("num_batteries", 0)
            battery_info = st.session_state.calculations.get("battery_info", {})
            required_solar = st.session_state.calculations.get("required_solar", 0)
            num_panels = st.session_state.calculations.get("num_panels", 0)
            panel_info = st.session_state.calculations.get("panel_info", {})
            controller_current = st.session_state.calculations.get("controller_current", 0)
            selected_controller = st.session_state.calculations.get("selected_controller", "")
            inverter_size = st.session_state.calculations.get("inverter_size", 0)
            selected_inverter = st.session_state.calculations.get("selected_inverter", "")
            inverter_info = st.session_state.calculations.get("inverter_info", {})
            
            battery_cost = st.session_state.calculations.get("battery_cost", 0)
            solar_cost = st.session_state.calculations.get("solar_cost", 0)
            inverter_cost = st.session_state.calculations.get("inverter_cost", 0)
            controller_cost = st.session_state.calculations.get("controller_cost", 0)
            installation_cost = st.session_state.calculations.get("installation_cost", 0)
            wiring_cost = st.session_state.calculations.get("wiring_cost", 0)
            total_cost = st.session_state.calculations.get("total_cost", 0)
            
            # Create a simple text-based PDF
            pdf_content = f"""
            {'='*70}
            {COMPANY.upper()}
            {'='*70}
            {MOTTO}
            
            CLIENT INFORMATION
            {'='*70}
            Name: {client_name}
            Address: {client_address}
            Phone: {client_phone}
            Email: {client_email if client_email else "Not provided"}
            Location: {project_location}
            Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
            Quote Reference: ANNUR-{datetime.datetime.now().strftime('%Y%m%d')}-001
            
            LOAD AUDIT SUMMARY
            {'='*70}
            """
            
            for item in st.session_state.load_data:
                pdf_content += f"""
            {item['appliance']} - {item['watt']}W × {item['quantity']} × {item['hours']}h = {item['wh']} Wh/day"""
            
            pdf_content += f"""
            
            Total Energy Demand: {total_wh} Wh/day
            Total Power Demand: {total_watt} W
            
            SYSTEM SIZING
            {'='*70}
            Backup Time: {backup_time} hours
            Battery Voltage: {battery_voltage}V
            Depth of Discharge: {dod_limit}%
            Temperature Derating: {temperature_factor}%
            
            Battery Capacity: {battery_capacity_ah:.0f} Ah
            Battery Type: {battery_type}
            Number of Batteries: {num_batteries:.1f}
            
            Required Solar Capacity: {required_solar:.0f} W
            Solar Panel Type: {panel_type}
            Number of Panels: {num_panels:.1f}
            Sun Hours: {sun_hours} hours/day
            System Efficiency: {system_efficiency}%
            
            Charge Controller Size: {controller_current:.0f} A
            Recommended Controller: {selected_controller}
            
            Inverter Size: {inverter_size:.0f} W
            Recommended Inverter: {selected_inverter}
            
            FINANCIAL ANALYSIS
            {'='*70}
            Battery Cost: ₦{battery_cost:,.0f}
            Solar Panel Cost: ₦{solar_cost:,.0f}
            Inverter Cost: ₦{inverter_cost:,.0f}
            Charge Controller Cost: ₦{controller_cost:,.0f}
            Installation Cost: ₦{installation_cost:,.0f}
            Wiring & Accessories: ₦{wiring_cost:,.0f}
            {'-'*70}
            TOTAL SYSTEM COST: ₦{total_cost:,.0f}
            
            FINANCIAL ANALYSIS
            {'='*70}
            Monthly Energy Consumption: {monthly_energy_kwh:.1f} kWh
            Monthly Savings: ₦{monthly_savings:,.0f}
            Annual Savings: ₦{annual_savings:,.0f}
            Payback Period: {payback_period:.1f} years
            ROI over {system_lifespan} years: {roi:.0f}%
            
            TERMS & CONDITIONS
            {'='*70}
            Quote Validity: 30 days from date of issue
            Warranty: Equipment as per manufacturer warranty + 1 year workmanship
            Payment Terms: 50% advance, 50% upon completion
            Installation Timeline: 5-7 working days after material availability
            Service: 6 months free maintenance included
            
            {COMPANY} | {PHONE} | {EMAIL} | {WEBSITE}
            {ADDRESS}
            
            Thank you for choosing Annur Tech - Powering Nigeria's Future!
            """
            
            buffer.write(pdf_content.encode('utf-8'))
            buffer.seek(0)
            return buffer

        # Generate PDF button
        if st.button("📄 Generate Professional Quotation PDF", use_container_width=True, key="generate_pdf_btn"):
            with st.spinner("Generating professional quotation..."):
                st.session_state.pdf_data = create_professional_pdf()
                st.success("Professional quotation generated successfully!")
        
        # Download button (always visible if PDF data exists)
        if st.session_state.pdf_data is not None:
            st.download_button(
                "📥 Download Professional Quotation", 
                data=st.session_state.pdf_data, 
                file_name=f"AnnurTech_Quotation_{client_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf", 
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf_btn"
            )
        else:
            st.info("Click the 'Generate Professional Quotation PDF' button above to create your report.")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown(f"""
<div class="footer">
    {COMPANY} | {PHONE} | {EMAIL}<br>
    {ADDRESS}<br>
    © {datetime.datetime.now().year} Annur Tech Solar Solutions - Powering Nigeria's Future
</div>
""", unsafe_allow_html=True)
