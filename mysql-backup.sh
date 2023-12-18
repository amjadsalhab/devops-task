

SHOW_USAGE_HELP() {
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo " "
    echo "Options:"
    echo " "
    echo " [Required]   --environment  (ex: production,staging)"
    echo " [Required]   --mode  (ex: full,custom)"
    echo " [Required]   --database (ex: orders,users)"
    echo " [Required]   --creds-file-path (ex: ./staging.cnf)"
    echo " [Optional]   --tables (list of commma separated tables names ex users,roles)"
    echo ""
    echo "                  --help for help"
    exit 1
}

POSITIONAL=()
while [ $# -gt 0 ]; do
    KEY="$1"
    case $KEY in
    --environment) ENVIRONMENT="$2" ;shift;shift;;
    --mode) MODE="$2" ;shift;shift;;
    --database) DATABASE_NAME="$2" ;shift;shift;;
    --creds-file-path) CREDS_FILE_PATH="$2" ;shift;shift;;
    --tables) TABLES="$2" ;shift;shift;;
    *)
        SHOW_USAGE_HELP
        shift
        ;;
    esac
done

#Validating the input parameters
if [ -z "${ENVIRONMENT}" ] || [ -z "${MODE}" ] || [ -z "${DATABASE_NAME}" ] || [ -z "${CREDS_FILE_PATH}" ]; then
    SHOW_USAGE_HELP
fi

if [ "$MODE" == "custom" ] && [ -z "${TABLES}" ]; then
    echo "With Custom mode, please enter the tables names"
    echo "Exiting .."
    exit 99
fi


export MYSQL_TEST_LOGIN_FILE="$CREDS_FILE_PATH"
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M-%S")
if [ "$MODE" = "full" ]; then
    echo "Running in full mode"
    mysqldump --databases $DATABASE_NAME > full.sql
    tar -czvf full.tar.gz full.sql
    echo "uploading full dump to s3"
    aws s3 cp full.tar.gz s3://devops-mysql-dumps/${DATABASE_NAME}/${ENVIRONMENT}/${TIMESTAMP}-full.tar.gz
elif [ "$MODE" = "custom" ]; then
    echo "Running in custom mode"
    mkdir -p custom 
    IFS=','
    for TABLE in $TABLES
    do
        mysqldump $DATABASE_NAME $TABLE > ./custom/$TABLE.sql
    done
    tar -czvf custom.tar.gz -C custom .
    aws s3 cp custom.tar.gz s3://devops-mysql-dumps/custom/${ENVIRONMENT}/${DATABASE_NAME}/${TIMESTAMP}.tar.gz
else
    echo "Invalid mode"
fi