node ('nxt'){
    stage "Checkout"
    checkout scm

    stage "Build python 3"
    sh "python3 bootstrap.py"
    sh "bin/buildout || bin/buildout -vvvvv"
    sh "bin/develop up"

    stage "Pep 8"
    sh "if bin/pep8 lizard_connector > pep8.txt; then echo 'pep8 is a success'; else cat pep8.txt; false; fi"

    stage "Test python 3"
    sh "bin/test"

=begin
    We skip this step for now. Cause buildout doesn't seem to install mock.
    stage "Build python 2"
    sh "python bootstrap.py"
    sh "bin/buildout -vvvvv || bin/buildout -vvvvv"
    sh "bin/develop up"

    stage "Test python 2"
    sh "bin/test"
=end

}
