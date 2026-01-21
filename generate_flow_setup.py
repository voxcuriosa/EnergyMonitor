
def generate_flow_setup_script():
    # IDs
    VVB_ID = "cdcc332f-8002-4de1-845a-878407d3e291"
    
    js_code = f"""
// HomeyScript: Setup 'Smart VVB Control' Flow
// This script creates the flow that connects the Cron trigger to the Calculation Script.

async function setupSmartFlow() {{
    const flowName = "Smart VVB Control (Auto)";
    const vvbId = '{VVB_ID}';
    const scriptName = 'check_avg_power'; // MUST MATCH the name you saved the previous script as!
    
    console.log(`Creating Flow: ${{flowName}}...`);

    try {{
        const flowDefinition = {{
            name: flowName,
            enabled: true,
            trigger: {{
                // Trigger: Every 1 Minute
                uri: 'homey:manager:cron',
                id: 'minute', // Standard cron trigger
                args: {{}}
            }},
            conditions: [
                {{
                    // Condition: Run HomeyScript
                    // We need to find the specific card URI for HomeyScript "Run with result"
                    // Usually: homey:app:com.athom.homeyscript:condition
                    uri: 'homey:app:com.athom.homeyscript', 
                    id: 'condition', // 'condition' is the ID for "Run a script" that returns boolean
                    args: {{
                        code: scriptName, // The argument name for the script reference. 
                        // Note: Depending on version, this might be 'script' or 'code'.
                        // We will try 'script' first as it refers to a saved script.
                        // If it fails, you might need to check the card arguments.
                        script: scriptName 
                    }}
                }}
            ],
            actions: [
                {{
                    // Action 1: Turn Off VVB
                    uri: 'homey:device:action:turn_off', 
                    id: 'turn_off',
                    args: {{
                        device: vvbId
                    }}
                }},
                {{
                    // Action 2: Turn On VVB after 20 mins
                    uri: 'homey:device:action:turn_on',
                    id: 'turn_on',
                    delay: 1200000, 
                    args: {{
                        device: vvbId
                    }}
                }}
            ]
        }};

        // API V3 requires {{ flow: ... }} wrapper
        const flow = await Homey.flow.createFlow({{ flow: flowDefinition }});

        console.log("✅ Flow Created Successfully!");
        console.log("🔗 Trigger: Every 1 Minute");
        console.log(`🔗 Condition: Run Script '${{scriptName}}'`);
        console.log("🔗 Action: Turn VVB Off -> On (20m delay)");
        
        return flow;

    }} catch (err) {{
        console.error("❌ Error creating flow:", err);
        console.log("💡 Tip: Ensure you have the 'HomeyScript' app installed.");
        console.log("💡 Tip: Ensure you saved the calculation script exactly as '" + scriptName + "'");
    }}
}}

await setupSmartFlow();
"""
    return js_code

if __name__ == "__main__":
    script_content = generate_flow_setup_script()
    output_file = "setup_smart_flow.js"
    with open(output_file, "w") as f:
        f.write(script_content)
    print(f"✅ Generated HomeyScript: {output_file}")
