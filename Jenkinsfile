pipeline {
    agent none
    parameters {
        string(name: 'SERVICE_NAME', defaultValue: 'orders', description: 'Service name to be deployed')
        string(name: 'SERVICE_PATH', defaultValue: 'orders', description: 'Service path in repo')
        string(name: 'ENVIRONMENT', defaultValue: 'production', description: 'Target Environment')

    }
    environment {
        ECR_REGISTRY = "472246201927.dkr.ecr.us-east-1.amazonaws.com/$ENVIRONMENT-$SERVICE_NAME"
        ECS_CLUSTER = "$ENVIRONMENT-cluster"
        ECS_TASK_DEFENETION = "$ENVIRONMENT-$SERVICE_NAME"
        ECS_SERVICE = "$SERVICE_NAME"
        AWS_DEFAULT_REGION = "us-east-1"
        TIMEOUT = 600
        INTERVAL = 5

    }
    stages {
       stage('General Information' ) {
            agent { node 'default' }
            steps {
                script {
                    sh '''
                        echo "Target environment is $ENVIRONMENT"
                        echo "Target Service is $SERVICE_NAME"
                        echo "ECR Registy is $ECR_REGISTRY"
                        echo "ECS Cluster is $ECS_CLUSTER"
                        echo "ECS Task Defention is $ECS_TASK_DEFENETION"
                        echo "Commit ID is $GIT_COMMIT"
                    '''
                    //slackSend color: 'good', channel: 'deployment-notifications', failOnError: true, message: "${env.ENVIRONMENT} ${env.SERVICE_NAME} - deployment started - ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
                }
            } 
        }
        stage('Build Container Image' ) {
            agent { label 'kaniko' }
            steps {
                script {
                    sh '''
                    /kaniko/executor --dockerfile ${PWD}/${SERVICE_PATH}/Dockerfile \
                              --context ${PWD}/${SERVICE_PATH} \
                              --destination="$ECR_REGISTRY:$GIT_COMMIT" \
                              --build-arg ENVIRONMENT=$ENVIRONMENT \
                              --verbosity error
                    '''
                }
            } 
        }
        
        stage('Deploy to AWS ECS' ) {
           agent { label 'aws-cli' }
            steps {
                script {
                    sh '''
                    #!/bin/bash
                    NEW_IMAGE=${ECR_REGISTRY}:${GIT_COMMIT}
                    TASK_DEFINITION=$(aws ecs describe-task-definition --task-definition "$ECS_TASK_DEFENETION")

                    NEW_TASK_DEFINITION=$(echo $TASK_DEFINITION | jq --arg IMAGE "$NEW_IMAGE" '.taskDefinition | .containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.compatibilities) | del(.registeredAt) | del(.registeredBy)')
                    NEW_REVISION=$(aws ecs register-task-definition --cli-input-json "$NEW_TASK_DEFINITION")
                    NEW_REVISION_NUMBER=$(echo $NEW_REVISION | jq '.taskDefinition.revision')
                    TASK_DEFINITION_ARN=$(echo $NEW_REVISION | jq -r '.taskDefinition.taskDefinitionArn')

                    echo "New revision: $NEW_REVISION_NUMBER created for task definition: $ECS_TASK_DEFENETION with image: $NEW_IMAGE"

                    echo $TASK_DEFINITION_ARN
                    aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" --task-definition "$TASK_DEFINITION_ARN"
                    '''
                }
            } 
        }

        stage('Wait Servie To Rollout' ) {
            agent { label 'aws-cli' }
            steps {
                script {
                    sh '''
                    set +x
                    echo "Started: Time=$(date), Timeout=$TIMEOUT seconds\n"
                    START_TIME=$(date +%s)
                    while true; do
                        SERVICE=$(aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE)
                        [ "true" = "$(echo $SERVICE | jq '.services | length > 0')" ] || exit 404 #service not found

                        NUM_PRIMARY=$(echo $SERVICE | jq '[ .services[].deployments[] | select(.status == "PRIMARY") | .runningCount ] | add // 0' --raw-output)
                        NUM_DESIRED=$(echo $SERVICE | jq '.services[].desiredCount' --raw-output)
                        NUM_TOTAL=$(echo $SERVICE | jq '[ .services[].deployments[] | .runningCount ] | add // 0' --raw-output)
                        ELAPSED=$(($(date +%s) - START_TIME))

                        echo "Deployment task counts: Primary=$NUM_PRIMARY, Desired=$NUM_DESIRED, Total=$NUM_TOTAL; Elapsed: $ELAPSED seconds"

                        # desrired == active
                        if [ "true" = "$(echo $SERVICE | jq '([.services[].deployments[]] | length == 1) and ([.services[].deployments[] | select(.runningCount == .desiredCount)] | length == 1)')" ]; then
                            echo "Deployment finished.\n"
                            exit 0
                        elif [ $ELAPSED -gt $TIMEOUT ]; then
                            exit 504
                        else
                            sleep $INTERVAL
                        fi
                    done
                    '''
                }
            } 
        }       
    }
    /*
    post {
        always {
            cleanWs()
        }
        
        success {
            slackSend color: 'good', channel: 'deployment-notifications', failOnError: true, message: "${env.ENVIRONMENT} ${env.SERVICE_NAME} - Deployed successfully! :heavy_check_mark: :tada: - ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        failure {
            slackSend color: 'danger', channel: 'deployment-notifications', failOnError: true, message: "${env.ENVIRONMENT} ${env.SERVICE_NAME} - Build failed :x: - ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        
    }
    */ 
}
