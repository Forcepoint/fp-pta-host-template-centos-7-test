pipeline {
    agent {
        label 'pta-controller'
    }
    triggers {
        // Run between 1 AM and 4 AM on Monday.
        cron('H 1-3/3 * * 1')
    }
    parameters {
        string(name: 'PACKER_VM_NAME', defaultValue: 'template-pta-centos-7-test', description: 'The name to give the produced VM.')
        string(name: 'PACKER_ARTIFACTORY_DNS', defaultValue: '', description: 'The DNS name of the Artifactory instance to use for proxies instead of going to the internet.')
        booleanParam(name: "TestSystems", defaultValue: true, description: 'Reprovision the associated TestSystems.')
    }
    environment {
        // This is the SSH pub key on the box running Ansible. It needs to be on all the provisioned VMs so Ansible can connect to them.
        // If you change the SSH pub and private keys on the box running Ansible, you'll have to update this.
        PACKER_SSH_PUB = "ssh-rsa AAAABBBBBBBBBBBCCCCCCCCCDDDDDDDDDDEEEEEEEEEEEFFFFFFFFFFFGGGGGGGGGGGGGGHHHHHHHHHHHHIIIIIIIIIIIJJJJJJJJJKKKKKKKKKKKK=="
        PACKER_TIMEZONE = "US/Mountain"
        PACKER_HOST_NAME = "PTATemplate"
    }
    options {
        disableConcurrentBuilds()
    }
    stages {
        stage('Populate Config with Secrets') {
            agent {
                label 'packer'
            }
            steps {
                dir ("cfg") {
                    sh '''
                        /opt/rh/rh-python36/root/usr/bin/virtualenv virt_pylint
                        source virt_pylint/bin/activate
                        pip install -r requirements.txt
                        pylint render_cfg.py --max-line-length=120
                        deactivate
                       '''
                    withCredentials(
                            [usernamePassword(credentialsId: 'pta-user-root', usernameVariable: 'PACKER_CENTOS7_ROOT_NAME', passwordVariable: 'PACKER_CENTOS7_ROOT_PASSWORD'),
                             usernamePassword(credentialsId: 'pta-user-service', usernameVariable: 'PACKER_CENTOS7_USER_NAME', passwordVariable: 'PACKER_CENTOS7_USER_PASSWORD')]) {
                        sh '''
                            source virt_pylint/bin/activate
                            python render_cfg.py
                            deactivate
                           '''
                    }
                }
            }
        }
        stage('Run Packer') {
            agent {
                label 'packer'
            }
            steps {
                withCredentials(
                        [usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'PACKER_VSPHERE_USER', passwordVariable: 'PACKER_VSPHERE_PASSWORD'),
                         usernamePassword(credentialsId: 'pta-user-root', usernameVariable: 'PACKER_CENTOS7_ROOT_NAME', passwordVariable: 'PACKER_CENTOS7_ROOT_PASSWORD')]) {
                    // For extra logging, adding "PACKER_LOG=1" to the start of the shell command below.
                    // To keep the VM running for inspection, add -on-error=abort
                    sh "packer build -color=false -force centos7.json"
                }
            }
        }
        stage('TestSystems') {
            when {
                expression { params.TestSystems }
            }
            steps{
                build job: 'PTA-Hosts/TestSystems-centos-7', propagate: false, wait: true, parameters: [
                        booleanParam(name: 'Terraform_Apply', value: true),
                        booleanParam(name: 'Terraform_Verify', value: false),
                        booleanParam(name: 'Ansible', value: true)]
            }
        }
    }
    post {
        failure {
            emailext body: '''$PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS<br><br>Check the console output at ${BUILD_URL}console to view the results.''', mimeType: 'text/html', recipientProviders: [requestor()], subject: '$PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS!', to: "pta.admin@company.com"
        }
    }
}