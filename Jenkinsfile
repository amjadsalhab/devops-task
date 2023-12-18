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

    }
    stages {
       stage('General Information' ) {
            agent { node 'aws-cli' }
            steps {
                script {
                    sh '''
                        echo "Target environment is $ENVIRONMENT"
                        echo "Target Service is $SERVICE_NAME"
                        echo "ECR Registy is $ECR_REGISTRY"
                        echo "ECS Cluster is $ECS_CLUSTER"
                        echo "ECS Task Defention is $ECS_TASK_DEFENETION"
                        echo "Commit ID is $COMMIT_ID"
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
                              --destination="$ECR_REGISTRY" \
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
                    yarn $BUILD_COMMAND
                    ls -al build
                    '''
                }
            } 
        }

        stage('Wait Servie To Rollout' ) {
            agent { label 'aws-cli' }
            steps {
                script {
                    sh '''
                    yarn $BUILD_COMMAND
                    ls -al build
                    '''
                }
            } 
        }       
    }
    
    post {
        always {
            cleanWs()
        }
        /*
        success {
            slackSend color: 'good', channel: 'deployment-notifications', failOnError: true, message: "${env.ENVIRONMENT} ${env.SERVICE_NAME} - Deployed successfully! :heavy_check_mark: :tada: - ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        failure {
            slackSend color: 'danger', channel: 'deployment-notifications', failOnError: true, message: "${env.ENVIRONMENT} ${env.SERVICE_NAME} - Build failed :x: - ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        */
    }
    
   
   
}
