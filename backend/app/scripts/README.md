# List of commands to run the scripts in sequence
# Ensure you have the necessary environment variables set in your .env file

# Step 1: Generate PRD
python app/scripts/step1_generate_prd.py

# Step 2: Generate TSD
python app/scripts/step2_generate_tsd.py

# Step 3: Generate TRD
python app/scripts/step2_generate_trd.py

# Step 4: Generate Tasks using Task Master
python app/scripts/step4_generate_tasks.py

# Step 5: Generate Jira Tasks
python app/scripts/step5_generate_jira_tasks.py

# Step 6: Generate Gnatt Chart
python app/scripts/step5_generate_gnatt_chart.py <Path of tasks.json> ./docs/gantt_chart.html 