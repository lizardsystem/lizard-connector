node ('nxt'){
    stage "Checkout"
    checkout scm

    stage "Pep 8"
    sh "if bin/pep8 lizard_connector > pep8.txt; then echo 'pep8 is a success'; else cat pep8.txt; false; fi"

    stage "Build python 3"
    sh "pip3 install pip --upgrade"
    sh "pip3 install setuptools --upgrade"
    sh "python3 bootstrap.py"
    sh "bin/buildout -vvvvv"

    stage "Test python 3"
    sh "bin/test"

    stage "Build python 2"
    sh "python bootstrap.py"
    sh "bin/buildout -vvvvv"
    sh "bin/develop up"

    stage "Test python 2"
    sh "bin/test"
}
