#!/usr/bin/env groovy

pipeline {
    agent {
        label params.SLAVE_LABEL
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    environment{
        VAULT_FILE = credentials('ams_vault_password')
    }

    parameters {
        choice(
            name: 'ENV',
            choices: ['dev','staging', 'production'],
            description: 'This is used to determine test env to dopeloy on (prod,staging,dev). DEV will create local Maria DB install, prod, staging will use and existing MARIA DB and will make migrations'
        )
        
        string(name: 'SLAVE_LABEL', defaultValue: 'AMS', description: 'Specify the slave label that you want the job to run on')
        
        booleanParam( 
            defaultValue: false, 
            description: 'If set to true run MARIA DB Backup', 
            name: 'BACKUP_DB'
        )

        booleanParam( 
            defaultValue: false, 
            description: 'If set to true forcibly recreates MARIA DB container', 
            name: 'RECREATE_DB'
        )

        booleanParam( 
            defaultValue: false, 
            description: 'If set to true run image will pushed to the arm.docker', 
            name: 'PUSH_TO_DOCKER_REGISTRY'
        )
    }

    stages {
	    stage('Set build name') {
            steps {
                script {
                    setEnvs()
                    currentBuild.displayName = "${env.BUILD_NUMBER} - ${params.ENV} - ${env.BRANCH_NAME} - ${env.VERSION}"
                }
            }
        }

        stage('Build Docker') {
            steps {
                echo "Using $env.ENV_PATH"    
                decryptFiles()      
                sh "docker build -t ams:$VERSION ."
            }
        }

        stage ('Backup Maria DB'){
            when {
                expression {"${params.BACKUP_DB}" == 'true' }
            }
            steps{
                echo "Maria DB backup"
                build job: 'AMS_backup', parameters: [string(name: 'ENV', value: "${params.ENV}"), string(name: 'TYPE', value: 'full')]
            }
        }

        stage('Run Maria DB') {
            steps{
                echo "Running Maria DB if not running"
                runMariaContainer()
                sh"sleep 20"
                createMariaSchema()
            }
            // post{
            //     success{
            //         archiveArtifacts allowEmptyArchive: true, artifacts: "${params.DEPLOYMENT_NAME}_cert_list.txt", followSymlinks: false
            //     }
            // }
        }

        stage('Run AMS') {
            steps{
                echo "Udpate env files"
                sh "sed -i \"s/VERSION/${version}/g\" ${ENV_PATH}/docker-compose.yaml" 
                sh "mkdir -p /var/container_data/AMS/env/$params.ENV"
                sh "cp -r ${ENV_PATH}/* /var/container_data/AMS/env/$params.ENV/ "                
                echo "Launching the APP"
                sh "docker-compose -f /var/container_data/AMS/env/$params.ENV/docker-compose.yaml up -d "
                sh "sleep 10"
                sh "docker restart ams-$params.ENV"

            }
            // post{
            //     success{
            //         archiveArtifacts allowEmptyArchive: true, artifacts: "${params.DEPLOYMENT_NAME}_cert_list.txt", followSymlinks: false
            //     }
            // }
        }

        stage('Run TEST') {
            steps{
                echo "Running TEST"
            }
            // post{
            //     success{
            //         archiveArtifacts allowEmptyArchive: true, artifacts: "${params.DEPLOYMENT_NAME}_cert_list.txt", followSymlinks: false
            //     }
            // }
        }

        stage ("Push to docker registry"){
            when {
                expression {"${params.PUSH_TO_DOCKER_REGISTRY}" == 'true' }
            }
            steps{
                echo "Releasing image to docker registry"
            }
        }


    }
    post {
        always{
            cleanWs disableDeferredWipeout: true
            sh "docker container prune -f"
            sh "docker image prune -f"
        }
    }
}

def setEnvs(){
    switch (params.ENV){
        case 'production':
            echo "Running on Prod"
            env.ENV_PATH = "ci/jenkins/files/env/prod"
            env.DB_PASSWORD = "Bu1ZMX1ZE5TwzsWQT2SaLVX5hGyWIXUz26EbDAP01w922xrBvkFZEpW4wHbOwP5m"
            break
        case 'staging':
            echo "Running on Staging"
            env.ENV_PATH = "ci/jenkins/files/env/stg"
            env.DB_PASSWORD = "rWt7U9IrQfpInrG6CBGfBUk7lmo6EVMcv3gE3rdCjD4PVPilEB6MZU1vvHpKLOCH"
            break
        case 'dev':
            echo "Running on Dev"
            env.ENV_PATH = "ci/jenkins/files/env/dev"
            env.DB_PASSWORD = "example"
            break
            
    }

    env.VERSION = sh (returnStdout: true, script:"cat VERSION").trim() 

}

def decryptFiles(){
  sh"""
    ansible-vault decrypt ams/ams/settings.py --vault-password-file=$VAULT_FILE

    for i in {dev,prod,stg}; do
        ansible-vault decrypt ci/jenkins/files/env/\$i/docker-compose.yaml --vault-password-file=$VAULT_FILE
    ansible-vault decrypt ci/jenkins/files/env/\$i/settings.py --vault-password-file=$VAULT_FILE
    done
  """
}

def runMariaContainer(){
    echo "Running Maria DB container"
    if ("${params.RECREATE_DB}" == 'true'){
        echo "Stopping Maria"
        sh "docker-compose  -f /var/container_data/AMS/env/$params.ENV/docker-compose.yaml stop maria-ams-$params.ENV"
        echo "Clearing Maria container"
        sh "docker-compose  -f /var/container_data/AMS/env/$params.ENV/docker-compose.yaml rm -f maria-ams-$params.ENV"
    }

    echo "Starting Maria DB"
    sh "docker-compose  -f /var/container_data/AMS/env/$params.ENV/docker-compose.yaml up -d maria-ams-$params.ENV"
    
}

def createMariaSchema(){
    echo "Creating Maria DB schema"
    sh "docker cp ${ENV_PATH}/schema.sql maria-ams-$params.ENV:/tmp/"
    sh "docker exec maria-ams-$params.ENV  bash -c \"mysql -u root -p$DB_PASSWORD < /tmp/schema.sql\" "
}

def runAMSContainer(){
    echo "Running Maria DB container"
    sh "docker-compose  -f /var/container_data/AMS/env/$params.ENV/docker-compose.yaml up -d ams-$params.ENV"
}