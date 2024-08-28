CCD Release Automation for FlexiKube
====================================

### Cloud Container Distribution Pre-provisioned - CXP 903 6304 R31B

This repo is used to maintain CCD pre-provisioned Ansible automation delivered by CCD for
each release.

Any bug-fixes and FlexiKube customisations are applied on top of the release automation.

Only the `ansible` directory is stored in this repo.

The master branch will always be an exact match of the latest CCD released files. We create versioned branches for each release and any patches or fixes are made to these versioned branches.

### Steps to prepare for a new CCD release

When CCD provides a new release, we download and extract the release and copy the ansible directory to the repo. We also create the new versioned branch.

1. Checkout to master branch

        $ git checkout master

2. Replace all files with new CCD release files (only ansible dir)

        $ rm -r ansible/
        $ cp -pr /path/to/ccd/eccd-2.35.0-001607-dccc64/ansible .
        $ git add .

3. Commit and push for review *without* making any changes to files

        $ git commit -m 'CCD 2.35.0 release'
        $ git push origin HEAD:refs/for/master

4. Once merged to master, create version branch

        $ git push --set-upstream origin 2.35.0

### Steps to patch a versioned branch

Any fixes for a particular release must be done on the versioned branch, never master branch.

1. Checkout versioned branch and make changes on top

        $ git checkout 2.35.0

2. Commit and push for review

        $ git commit -m 'CCD 2.35.0 fixes'
        $ git push origin HEAD:refs/for/2.35.0


Links
-----

CCD releases (pre-provisioned: CXP9036304): https://arm.sero.gic.ericsson.se/artifactory/proj-erikube-generic-local/erikube/releases

