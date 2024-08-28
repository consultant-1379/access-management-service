#!/usr/bin/env groovy

pipeline {
    agent {
        label params.SLAVE_LABEL
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    parameters {
        choice(
            name: 'ENV',
            choices: ['dev','staging', 'production'],
            description: 'This is used to determine test env to dopeloy on (prod,staging,dev). DEV will create local Maria DB install, prod, staging will use and existing MARIA DB and will make migrations'
        )

        choice(
            name: 'TYPE',
            choices: ['full', 'incremental'],
            description: 'This is used to determine test env to dopeloy on (prod,staging,dev). DEV will create local Maria DB install, prod, staging will use and existing MARIA DB and will make migrations'
        )

        string(name: 'BCK_ROTATION_DAYS', defaultValue: '30', description: 'Specify number of DAYS for backup to keep')       
        string(name: 'SLAVE_LABEL', defaultValue: 'AMS', description: 'Specify the slave label that you want the job to run on')
        string(name: 'MARIA_IMG', defaultValue: 'armdocker.rnd.ericsson.se/dockerhub-ericsson-remote/mariadb:10.7.8-focal', description: 'MARIA DB IMAGE USED for backups')
        
    }

    stages {
	    stage('Set build name') {
            steps {
                script {
                    setEnvs()
                    currentBuild.displayName = "${env.BUILD_NUMBER} - ${params.ENV} - ${env.VERSION} - backup - ${params.TYPE} "
                }
            }
        }

        stage ('Maria DB check'){

            steps{
                runMariaCheck()
            }
        }


        stage ('Backup Maria DB'){

            steps{
                script{
                    if ( "${params.TYPE}" == 'full'){
                        runMariaFullBackup()
                    }else{
                        runMariaIncrementalBackup()
                    }
                }
            }
        }

        stage('Run Maria DB test restore') {
            steps{
                runTestRestore()
            }
        }

        stage('Rotate old backups') {
            steps{
                rotateBackups()
            }
        }

    }
    post {
        always{
            cleanWs disableDeferredWipeout: true
            sh "docker container prune -f"
            sh "docker volume prune -f"
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

def runMariaCheck(){
    echo "Analyze Maria DB status"
    sh """ check_list="\$(docker exec maria-ams-$params.ENV  bash -c \"mariadb-check  --user=root --password=$DB_PASSWORD -A \")"
    if echo "\$check_list" | grep -v OK; then
        echo "DB CHECKS FAILED"
        exit 1
    fi
    """
    sh "docker exec maria-ams-$params.ENV  bash -c \"mariadb-analyze  --user=root --password=$DB_PASSWORD -A \" "
}

def runMariaFullBackup(){
    echo "Creating Maria DB Full backup"
    sh"docker exec maria-ams-$params.ENV  bash -c \"mkdir -p /backup/full/\""
    sh "docker exec maria-ams-$params.ENV  bash -c \"mariabackup --user=root --password=$DB_PASSWORD --backup --target-dir=/backup/full/${env.BUILD_NUMBER}-full_bck-\$(date +'%Y-%m-%d') \" "
}


def runMariaIncrementalBackup(){
    echo "Creating Maria DB incremental backup"
    sh """
        full_backup_name=\$(basename \$(docker exec maria-ams-$params.ENV  bash -c \"ls -td /backup/full/*/ | head -n 1\" ))
        echo "Creating inc backup for \$full_backup_name"
        docker exec maria-ams-$params.ENV  bash -c \"mkdir -p /backup/incremental/\$full_backup_name\"
        docker exec maria-ams-$params.ENV  bash -c \"mariabackup --user=root --password=$DB_PASSWORD --incremental-basedir=/backup/full/\$full_backup_name --backup --target-dir=/backup/incremental/\$full_backup_name/${env.BUILD_NUMBER}-inc_bck-\$(date +'%Y-%m-%d') \" 
    """
}

def runTestRestore(){
    echo "Creating temporary DB"
    sh """
        docker volume create backup-${env.BUILD_NUMBER}
        docker volume create data-${env.BUILD_NUMBER}
      
        docker run --rm -v /var/container_data/AMS/env/$params.ENV/maria/backup:/backup_orig/ -v backup-${env.BUILD_NUMBER}:/backup $params.MARIA_IMG bash -c \"cp -r /backup_orig/* /backup/ \"
        
        full_backup_name=\$(basename \$(docker exec maria-ams-$params.ENV  bash -c \"ls -td /backup/full/*/ | head -n 1\" ))
        docker run --rm  -v backup-${env.BUILD_NUMBER}:/backup $params.MARIA_IMG chown -R mysql:mysql /backup
        docker run --user mysql --rm  -v backup-${env.BUILD_NUMBER}:/backup $params.MARIA_IMG mariabackup  --prepare --target-dir=/backup/full/\$full_backup_name
        
    """

        if ( "${params.TYPE}" == 'full'){
            sh"""
                full_backup_name=\$(basename \$(docker exec maria-ams-$params.ENV  bash -c \"ls -td /backup/full/*/ | head -n 1\" ))
                echo "TEST RESTORING from full backup \$full_backup_name "
                docker run --user mysql --rm  -v backup-${env.BUILD_NUMBER}:/backup -v data-${env.BUILD_NUMBER}:/var/lib/mysql $params.MARIA_IMG mariabackup --copy-back --target-dir=/backup/full/\$full_backup_name
            """

        }else{
            sh """
                full_backup_name=\$(basename \$(docker exec maria-ams-$params.ENV  bash -c \"ls -td /backup/full/*/ | head -n 1\" ))
                inc_backups=\$( docker exec maria-ams-$params.ENV  ls backup/incremental/\$full_backup_name )
                echo "TEST RESTORING inc backups for \$full_backup_name: \$inc_backups"
                for i in \$inc_backups;do
                    docker run --user mysql --rm  -v backup-${env.BUILD_NUMBER}:/backup $params.MARIA_IMG mariabackup  --prepare --target-dir=/backup/full/\$full_backup_name --incremental-dir=/backup/incremental/\$full_backup_name/\$i
                done
                docker run --user mysql --rm  -v backup-${env.BUILD_NUMBER}:/backup -v data-${env.BUILD_NUMBER}:/var/lib/mysql $params.MARIA_IMG mariabackup --copy-back --target-dir=/backup/full/\$full_backup_name
            """
        }
    sh """   
        docker run --rm  -v data-${env.BUILD_NUMBER}:/var/lib/mysql $params.MARIA_IMG chown -R mysql:mysql /var/lib/mysql
        if  docker ps -a | grep maria-test ; then
            docker rm --force maria-test
        fi
       docker run --name maria-test  -v data-${env.BUILD_NUMBER}:/var/lib/mysql  -td $params.MARIA_IMG
       sleep 30
    """
    sh """
        if docker logs maria-test | grep -i error ; then 
        echo "BACKUP VALIDATION FAILED" 
        echo "Deleting created backup"
        full_backup_name=\$(basename \$(docker exec maria-ams-$params.ENV  bash -c \"ls -td /backup/full/*/ | head -n 1\" ))
                
            if [ "${params.TYPE}" = "full"];then
                echo "Full backup: \$full_backup_name"
                docker exec maria-ams-$params.ENV rm -rf /backup/full/\$full_backup_name
            else
                echo "Incremental backup: \$full_backup_name\$inc_backup_name"
                inc_backups=\$( docker exec maria-ams-$params.ENV  ls backup/incremental/\$full_backup_name )
                docker exec maria-ams-$params.ENV rm -rf /backup/incremental/\$full_backup_name/\$inc_backup_name
            fi
        exit 1 
        fi
    """
    sh "docker rm --force maria-test"
    sh "docker volume rm backup-${env.BUILD_NUMBER}"
    sh "docker volume rm data-${env.BUILD_NUMBER}"
}

def rotateBackups(){
    echo "Checking if full backup requires rotation"
    
    sh """
        delete_list=\$(docker exec maria-ams-$params.ENV find /backup/full/ -type d -mtime +${params.BCK_ROTATION_DAYS})
        echo "Deleting old backups:\n\$delete_list"
        for i in delete_list; do
            docker exec maria-ams-$params.ENV rm -rf /backup/full/\$i
            docker exec maria-ams-$params.ENV rm -rf /backup/incremental/\$i
        done
    """
}

