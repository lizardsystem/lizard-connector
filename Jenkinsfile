node ('nxt'){
    stage "Checkout"
    checkout scm

    stage "Build"
    sh "python bootstrap.py"
    sh "bin/buildout || bin/buildout"
    sh "bin/buildout -vvvvv"
    sh "bin/develop up"

    stage "Pep 8"
    sh "if bin/pep8 lizard_connector > pep8.txt; then echo 'pep8 is a success'; else cat pep8.txt; false; fi"

    stage "Test"
    sh "bin/test --noinput"
}
