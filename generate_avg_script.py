
def generate_avg_script():
    # IDs found via inspection
    TIBBER_ID = "5ea9f049-231c-400e-83f1-7ba40b3a6e45"
    VVB_ID = "cdcc332f-8002-4de1-845a-878407d3e291"
    
    js_code = f"""
// HomeyScript: Check 10-min Weighted Average Power
// Returns TRUE if Avg > 10,000 W AND VVB is currently ON.
// Usage: Run this in a Flow (e.g., every 1 min). If it returns True (True/False tag),
//        then execute: Turn VVB Off -> Delay 20 min -> Turn VVB On.

// 1. Configuration
const MAX_POWER = 10000; // 10 kW Limit
const TIME_WINDOW_MIN = 10; 

// Device IDs (Pre-filled)
const tibberId = '{TIBBER_ID}';
const vvbId = '{VVB_ID}';

async function checkPower() {{
    console.log("--------------- Power Check ---------------");

    // 2. Check VVB Status first (Fail fast)
    // If VVB is already OFF, we don't need to do anything (it's either paused or user turned it off)
    const vvbDevice = await Homey.devices.getDevice({{id: vvbId}});
    if (!vvbDevice) throw new Error("VVB Device not found");
    
    const isVvbOn = vvbDevice.capabilitiesObj?.onoff?.value;
    console.log(`VVB Status: ${{isVvbOn ? 'ON' : 'OFF'}}`);
    
    if (!isVvbOn) {{
        console.log("VVB is already OFF. No action needed.");
        return false; // Condition not met
    }}

    // 3. Get History for Tibber Power
    // We request 11 minutes to ensure we cover the full 10 min window including the start.
    const end = new Date();
    const start = new Date(end.getTime() - (TIME_WINDOW_MIN + 1) * 60 * 1000);
    
    // uri: 'homey:device:...' is not correct for getLog usually, we need the logic ID or similar.
    // Actually getLog uses the device object or specific URI structure.
    // The safest way in HomeyScript 2.0+ is using the device instance.
    
    const tibberDevice = await Homey.devices.getDevice({{id: tibberId}});
    if (!tibberDevice) throw new Error("Tibber Device not found");

    // Robust way: List ALL logs and find the right one
    const logsMap = await Homey.insights.getLogs();
    const allLogs = Object.values(logsMap); // getLogs returns an Object map, not Array
    
    // Filter for our device and capability
    // The logs usually contain a `uri` string which includes the device ID.
    // usage: l.id is 'homey:device:uuid:measure_power'
    // We prioritize measure_power, then energy_power
    let targetLog = allLogs.find(l => l.id.indexOf(tibberId) > -1 && l.id.endsWith('measure_power'));
    if (!targetLog) {{
        targetLog = allLogs.find(l => l.id.indexOf(tibberId) > -1 && l.id.endsWith('energy_power'));
    }}
    
    if (!targetLog) {{
        console.error("❌ Could not find Insight Log for 'measure_power'");
        // Debug: Print available logs for this device
        const deviceLogs = allLogs.filter(l => l.uri.includes(tibberId));
        console.log("Available logs for Tibber:", deviceLogs.map(l => l.id).join(', '));
        return false;
    }}

    console.log(`Found Log: ${{targetLog.uri}} / ${{targetLog.id}}`);

    
    // The entries returned by getLog might be the whole history or paginated? 
    // Usually it returns a default amount. We should specify range if possible, 
    // but the JS API signature is tricky. 
    // Let's filter manually if needed, or assume we get recent data.
    // Actually, `getLog` returns a LogEntry object which has a `getValues()` method.
    
    const historyStart = new Date(end.getTime() - TIME_WINDOW_MIN * 60 * 1000);
    
    // We found the metadata 'targetLog'.
    // Use getLogEntries directly with the identified log object.
    const dataObj = await Homey.insights.getLogEntries(targetLog, historyStart, end);
    
    // The API returns an object {{ values: [...], ... }} or sometimes array directly depending on version
    const data = Array.isArray(dataObj) ? dataObj : (dataObj.values || []);
    
    console.log(`Fetched ${{data.length}} data points from Tibber.`);
    
    if (data.length < 2) {{
        console.log("Not enough data to calculate average.");
        return false;
    }}

    // 4. Calculate Time-Weighted Average
    let totalWeightedPower = 0;
    let totalDuration = 0;
    
    for (let i = 0; i < data.length - 1; i++) {{
        const p1 = data[i];
        const p2 = data[i+1];
        
        // Value: p1.v, Time: p1.t (string or date)
        const t1 = new Date(p1.t).getTime();
        const t2 = new Date(p2.t).getTime();
        
        // Duration in seconds
        const duration = (t2 - t1) / 1000;
        
        if (duration <= 0) continue;
        
        // We assume linear interpolation or step? 
        // Tibber usually reports on change. Step is safer (value holds until next update).
        // Let's use the value of p1 for the duration.
        const avgVal = p1.v; 
        
        totalWeightedPower += avgVal * duration;
        totalDuration += duration;
    }}
    
    if (totalDuration === 0) return false;
    
    const weightedAverage = totalWeightedPower / totalDuration;
    console.log(`Time-Weighted Average (10 min): ${{weightedAverage.toFixed(0)}} W`);
    console.log(`Threshold: ${{MAX_POWER}} W`);
    
    if (weightedAverage > MAX_POWER) {{
        console.log("⚠️ THRESHOLD EXCEEDED! Suggesting VVB Pause.");
        return true; 
    }} else {{
        console.log("✅ Average below threshold.");
        return false;
    }}
}}

await checkPower();
"""
    return js_code

if __name__ == "__main__":
    script_content = generate_avg_script()
    output_file = "check_avg_power.js"
    with open(output_file, "w") as f:
        f.write(script_content)
    print(f"✅ Generated HomeyScript: {output_file}")
