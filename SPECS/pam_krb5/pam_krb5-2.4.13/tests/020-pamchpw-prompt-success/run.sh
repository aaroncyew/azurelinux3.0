#!/bin/sh

. $testdir/testenv.sh

echo "";echo Succeed: correct password, expired, change.
setpw $test_principal foo
pwexpire $test_principal now
test_settle
test_run -auth -account -setcred -session $test_principal $pam_krb5 $test_flags chpw_prompt -- foo bar bar
