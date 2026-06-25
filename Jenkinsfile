// Pipeline CI/CD FutureKawa — pipeline déclarative.
// Prérequis sur l'agent Jenkins : Docker CLI + plugin "docker compose" v2
// (voir CI_CD.md pour lancer Jenkins en local avec accès au démon Docker).
pipeline {
    agent any

    options {
        timestamps()                 // horodate chaque ligne de log (lisibilité jury)
        disableConcurrentBuilds()    // une exécution à la fois
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        // Tag d'image = numéro de build Jenkins (artefact traçable).
        IMAGE_TAG    = "${env.BUILD_NUMBER}"
        COUNTRY_DIR  = 'backend/backend-country'
        TEST_IMAGE   = 'futurekawa-backend-test'
        // Images produites par `docker compose build` (projet "futurekawa").
        IMG_COUNTRY  = 'futurekawa-backend-brazil'
        IMG_CENTRAL  = 'futurekawa-central'
        IMG_FRONTEND = 'futurekawa-frontend'
    }

    stages {

        // 1) Récupération du code -------------------------------------------------
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline || true'
            }
        }

        // 2) Build des images applicatives (backends, central, frontend) ----------
        stage('Build') {
            steps {
                echo 'Construction des images Docker via docker compose…'
                sh 'docker compose build backend-brazil central frontend'
            }
        }

        // 3) Tests pytest + rapport JUnit -----------------------------------------
        //    On construit une image de test, on l'exécute, on récupère TOUJOURS
        //    le rapport (même si des tests échouent), puis on fait échouer le build.
        stage('Test') {
            steps {
                script {
                    sh "docker build -t ${TEST_IMAGE} -f ${COUNTRY_DIR}/Dockerfile.test ${COUNTRY_DIR}"
                    sh 'docker rm -f fk-test-run >/dev/null 2>&1 || true'

                    // returnStatus : on capture le code sans interrompre la pipeline.
                    def code = sh(
                        script: 'docker run --name fk-test-run ${TEST_IMAGE}',
                        returnStatus: true
                    )

                    // Récupère le rapport JUnit hors du conteneur (preuve d'exécution).
                    sh "mkdir -p ${COUNTRY_DIR}/reports"
                    sh "docker cp fk-test-run:/app/reports/junit.xml ${COUNTRY_DIR}/reports/junit.xml || true"
                    sh 'docker rm -f fk-test-run >/dev/null 2>&1 || true'

                    if (code != 0) {
                        error("Échec des tests pytest (code de sortie ${code}) — voir le rapport JUnit.")
                    }
                }
            }
        }

        // 4) Qualité : linter Python (ruff, équivalent flake8) --------------------
        stage('Qualité') {
            steps {
                echo 'Analyse statique du code backend (ruff)…'
                // Réutilise l'image de test (ruff y est installé) ; échoue si lint KO.
                sh "docker run --rm ${TEST_IMAGE} ruff check ."
            }
        }

        // 5) Package : tag des images Docker comme artefacts ----------------------
        stage('Package') {
            steps {
                echo "Tag des images applicatives (tag ${IMAGE_TAG} + latest)…"
                sh '''
                    set -e
                    docker tag ${IMG_COUNTRY}  futurekawa/backend-country:${IMAGE_TAG}
                    docker tag ${IMG_COUNTRY}  futurekawa/backend-country:latest
                    docker tag ${IMG_CENTRAL}  futurekawa/backend-central:${IMAGE_TAG}
                    docker tag ${IMG_CENTRAL}  futurekawa/backend-central:latest
                    docker tag ${IMG_FRONTEND} futurekawa/frontend:${IMAGE_TAG}
                    docker tag ${IMG_FRONTEND} futurekawa/frontend:latest
                    echo "=== Images FutureKawa taggées ==="
                    docker images | grep futurekawa
                '''
            }
        }
    }

    // Gestion centralisée de la fin de pipeline -----------------------------------
    post {
        always {
            // Publie le rapport de tests dans l'UI Jenkins (onglet "Test Result").
            junit testResults: "${COUNTRY_DIR}/reports/junit.xml", allowEmptyResults: true
            // Archive le rapport comme artefact téléchargeable (preuve pour le jury).
            archiveArtifacts artifacts: "${COUNTRY_DIR}/reports/*.xml", allowEmptyArchive: true
        }
        success {
            echo '✅ Pipeline réussie : build, tests, qualité et package OK.'
        }
        failure {
            echo '❌ Pipeline en échec : consultez le stage fautif et le rapport de tests.'
        }
    }
}
