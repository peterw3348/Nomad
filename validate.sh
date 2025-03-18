#!/bin/bash

# Define color codes
RESET="\e[0m"
CYAN="\e[36m"    # Tool Name
GREEN="\e[32m"   # Passed
RED="\e[31m"     # Failed
BOLD="\e[1m"

# Track overall status
declare -A TOOL_RESULTS
EXIT_CODE=0

# Function to print centered tool headers
print_header() {
    TOOL_NAME=$1
    printf "\n${CYAN}${BOLD}===== %-20s =====${RESET}\n" "$TOOL_NAME"
}

# Function to run tools and store results
run_tool() {
    TOOL_CMD=$1
    TOOL_NAME=$2

    print_header "$TOOL_NAME"
    $TOOL_CMD
    if [ $? -eq 0 ]; then
        TOOL_RESULTS["$TOOL_NAME"]="${GREEN}Passed ✅${RESET}"
    else
        TOOL_RESULTS["$TOOL_NAME"]="${RED}Failed ❌${RESET}"
        EXIT_CODE=1
    fi
}

# Run tools
run_tool "black --check ." "Black Formatter"
run_tool "flake8 ." "Flake8 Linter"
run_tool "pydocstyle ." "Pydocstyle"
run_tool "pytest" "Pytest"

# Print summary
echo -e "\n${BOLD}===== Check Summary =====${RESET}"
for tool in "${!TOOL_RESULTS[@]}"; do
    echo -e "${BOLD}$tool Status: ${TOOL_RESULTS[$tool]}${RESET}"
done

# Exit with appropriate status
exit $EXIT_CODE
