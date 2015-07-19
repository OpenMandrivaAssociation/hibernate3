# Note that infinispan was removed in OpenMandriva "bootstrap" due to FTBFS
%{?_javapackages_macros:%_javapackages_macros}
%global namedreltag .Final
%global namedversion %{version}%{?namedreltag}
%global majorversion 3
%global oname hibernate-orm

Name:    hibernate3
Version: 3.6.10
Release: 15.2
Summary: Relational persistence and query service
Group:   Development/Java
License: LGPLv2+
URL:     http://www.hibernate.org/
# git clone git://github.com/hibernate/hibernate-orm
# cd hibernate-orm/ && git archive --format=tar --prefix=hibernate-orm-3.6.10.Final/ 3.6.10.Final | xz > hibernate-3.6.10.Final.tar.xz
Source0: hibernate-orm-3.6.10.Final.tar.xz
Source1: hibernate3-depmap
Patch0:  hibernate-orm-fix-cglib-gid.patch
Patch1:  hibernate-orm-fix-jacc-gid-aid.patch
Patch2:  hibernate-orm-fix-ant-gid.patch
Patch3:  hibernate-orm-infinispan-5-support.patch
Patch4:  hibernate-orm-cglib-3.1.patch

BuildArch: noarch

BuildRequires: jpackage-utils
BuildRequires: javapackages-tools >= 0.7.2
BuildRequires: java-devel
BuildRequires: maven-local
BuildRequires: maven-release-plugin
BuildRequires: maven-enforcer-plugin
BuildRequires: maven-injection-plugin
BuildRequires: antlr-maven-plugin
BuildRequires: geronimo-validation
BuildRequires: geronimo-jta
BuildRequires: hibernate-validator
BuildRequires: cglib
BuildRequires: jboss-jacc-1.4-api
BuildRequires: c3p0
BuildRequires: proxool
BuildRequires: hibernate-commons-annotations
BuildRequires: jboss-servlet-3.0-api
BuildRequires: ehcache-core
# jbosscache was retired
# BuildRequires: jbosscache-core
# BuildRequires: jbosscache-common-parent
# H3 dont support infinispan > 5.3.0
# BuildRequires: infinispan
BuildRequires: rhq-plugin-annotations
BuildRequires: h2
BuildRequires: mvn(hsqldb:hsqldb:1)
BuildRequires: mvn(org.slf4j:slf4j-log4j12)
BuildRequires: glassfish-jaxb
BuildRequires: shrinkwrap
BuildRequires: jboss-transaction-1.1-api

Obsoletes: %{name}-infinispan < %{version}-%{release}
Obsoletes: %{name}-jbosscache < %{version}-%{release}

%description
Hibernate is a powerful, ultra-high performance
object/relational persistence and query service
for Java.

%package javadoc
Summary: API docs for %{name}

%description javadoc
API documentation for %{name}.

%package entitymanager
Summary: Hibernate Entity Manager

%description entitymanager
%{summary}.

%package envers
Summary: Hibernate support for entity auditing

%description envers
%{summary}.

%package c3p0
Summary: C3P0-based implementation of Hibernate ConnectionProvider

%description c3p0
%{summary}.

%package proxool
Summary: Proxool-based implementation of Hibernate ConnectionProvder

%description proxool
%{summary}.

%package ehcache
Summary: Integration of Hibernate with Ehcache

%description ehcache
%{summary}.

%package testing
Summary: Hibernate JUnit test utilities

%description testing
%{summary}.

%prep
%setup -q -n %{oname}-%{namedversion}
%patch0 -p1
%patch1 -p1
%patch2 -p1
#%%patch3 -p1
%patch4 -p1

%pom_remove_plugin org.jboss.maven.plugins:maven-jdocbook-plugin hibernate-parent
%pom_remove_plugin org.jboss.maven.plugins:maven-jdocbook-style-plugin hibernate-parent
%pom_remove_plugin :gmaven-plugin hibernate-parent
%pom_disable_module hibernate-testsuite
%pom_disable_module hibernate-oscache
%pom_disable_module hibernate-swarmcache
%pom_disable_module hibernate-jdbc3-testing
%pom_disable_module hibernate-jdbc4-testing

%pom_disable_module hibernate-infinispan
%pom_disable_module hibernate-jbosscache

# Remove test deps infinispan jbosscache
for m in envers entitymanager ehcache; do
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:scope = 'test']" hibernate-${m}/pom.xml
done

# We don't need it
%pom_xpath_remove pom:build/pom:extensions hibernate-parent/pom.xml

# disable hibernate-tools support
%pom_remove_dep org.hibernate:hibernate-tools hibernate-envers
%pom_remove_dep ant:ant hibernate-envers
rm -r hibernate-envers/src/main/java/org/hibernate/tool/ant/*.java \
  hibernate-envers/src/main/java/org/hibernate/envers/ant/*.java

# Make hibernate-testing back a test dependency...
#sed -i "s|<!-- <scope>test</scope> TODO fix this -->|<scope>test</scope>|" hibernate-infinispan/pom.xml

# Fix the c3p0 gid
%pom_xpath_set "pom:project/pom:dependencies/pom:dependency[pom:artifactId = 'c3p0' ]/pom:groupId" com.mchange  hibernate-c3p0

# Fix the hibernate-commons-annotations gid
for f in hibernate-core hibernate-envers;do
%pom_xpath_set "pom:project/pom:dependencies/pom:dependency[pom:artifactId = 'hibernate-commons-annotations' ]/pom:groupId" org.hibernate.common  ${f}
done

for f in hibernate-core hibernate-entitymanager hibernate-parent;do
sed -i "s|<groupId>javax.validation|<groupId>org.apache.geronimo.specs|" ${f}/pom.xml
sed -i "s|<artifactId>validation-api|<artifactId>geronimo-validation_1.0_spec|" ${f}/pom.xml
done

sed -i "s|<groupId>javax.transaction|<groupId>org.jboss.spec.javax.transaction|" hibernate-core/pom.xml
sed -i "s|<artifactId>jta|<artifactId>jboss-transaction-api_1.1_spec|" hibernate-core/pom.xml
sed -i "s|<version>1.1</version>|<version>1.0.1.Final</version>|" hibernate-core/pom.xml

%pom_xpath_set "pom:project/pom:dependencyManagement/pom:dependencies/pom:dependency[pom:artifactId = 'hibernate-commons-annotations' ]/pom:groupId" org.hibernate.common  hibernate-parent

sed -i "s,59 Temple Place,51 Franklin Street,;s,Suite 330,Fifth Floor,;s,02111-1307,02110-1301," lgpl.txt

%mvn_compat_version : %{majorversion} %{namedversion}
%mvn_package ":hibernate-parent" %{name}
%mvn_package ":hibernate-core" %{name}
%mvn_package ":hibernate" __noinstall

%build

# Currently 4 tests fail with this error:
# "Unable to get the default Bean Validation factory"
export jdk16_home=/usr
export LANG=en_US.UTF-8
%mvn_build -s -f -- -DdisableDistribution=true

%install
%mvn_install

%files -f .mfiles-%{name}
%doc changelog.txt lgpl.txt
%dir %{_javadir}/%{name}

%files javadoc -f .mfiles-javadoc
%doc lgpl.txt

%files entitymanager -f .mfiles-hibernate-entitymanager
%doc lgpl.txt

%files envers -f .mfiles-hibernate-envers
%doc lgpl.txt

%files c3p0 -f .mfiles-hibernate-c3p0
%doc lgpl.txt

%files ehcache -f .mfiles-hibernate-ehcache
%doc lgpl.txt

%files proxool -f .mfiles-hibernate-proxool
%doc lgpl.txt

%files testing -f .mfiles-hibernate-testing
%doc lgpl.txt

%changelog
* Thu Jun 26 2014 gil cattaneo <puntogil@libero.it> 3.6.10-15
- disable jbosscache support

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.10-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 3.6.10-13
- Use Requires: java-headless rebuild (#1067528)

* Sat Sep 14 2013 gil cattaneo <puntogil@libero.it> 3.6.10-12
- rebuilt with new hibernate-commons-annotations
- fix validation-api gId:aId

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.10-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 10 2013 Marek Goldmann <mgoldman@redhat.com> - 3.6.10-10
- Removing test deps from poms
- Added geronimo-jta to R for hibernate-core

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.10-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 3.6.10-8
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Tue Oct 30 2012 Marek Goldmann <mgoldman@redhat.com> - 3.6.10-7
- Versioned jars to make it possible to install next to hibernate (4) package

* Mon Aug 20 2012 Marek Goldmann <mgoldman@redhat.com> - 3.6.10-6
- hibernate-testing should be a test dependency in infinispan module

* Sun Aug 12 2012 gil cattaneo <puntogil@libero.it> - 3.6.10-5
- Enable envers module
- Installed testing module (built but not installed)
- Disabled jdbc4-testing module
- Added maven fragments files in appropriate subpackages

* Fri Aug 10 2012 Andy Grimm <agrimm@gmail.com> - 3.6.10-4
- Enable jbosscache and infinispan modules (RHBZ#846658)
- Remove duplicate files from core package

* Mon Aug 06 2012 Andy Grimm <agrimm@gmail.com> - 3.6.10-3
- Enable ehcache module (#845209)
- Use pom macros for module disablement
- Split into subpackages

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Mar 14 2012 Andy Grimm <agrimm@gmail.com> - 3.6.10-1
- Initial package

