# Note that infinispan was removed in OpenMandriva "bootstrap" due to FTBFS
%{?_javapackages_macros:%_javapackages_macros}
%global namedreltag .Final
%global namedversion %{version}%{?namedreltag}
%global majorversion 3
%global oname hibernate-orm

Name:    hibernate3
Version: 3.6.10
Release: 12.1%{?dist}
Summary: Relational persistence and query service
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
BuildRequires: jbosscache-core
BuildRequires: jbosscache-common-parent
%if 0%{?fedora}
BuildRequires: infinispan
%endif
BuildRequires: rhq-plugin-annotations
BuildRequires: h2
%if 0%{?fedora}
%if %{fedora} > 19
BuildRequires: mvn(hsqldb:hsqldb:1)
%else
BuildRequires: mvn(hsqldb:hsqldb)
%endif
%else
BuildRequires: mvn(hsqldb:hsqldb:1)
%endif
BuildRequires: glassfish-jaxb
BuildRequires: shrinkwrap

Requires: java
Requires: jpackage-utils
Requires: javapackages-tools >= 0.7.2
Requires: apache-commons-collections
Requires: dom4j
Requires: geronimo-validation
Requires: hibernate-commons-annotations
Requires: hibernate-jpa-2.0-api
Requires: jboss-servlet-3.0-api
Requires: geronimo-jta

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
Requires: cglib
Requires: %{name} = %{version}-%{release}
Requires: hibernate-jpa-2.0-api
Requires: hibernate-validator
Requires: javassist

%description entitymanager
%{summary}.

%package envers
Summary: Hibernate support for entity auditing
Requires: hibernate-commons-annotations
Requires: hibernate-jpa-2.0-api
Requires: %{name} = %{version}-%{release}
Requires: %{name}-entitymanager = %{version}-%{release}

%description envers
%{summary}.

%package c3p0
Summary: C3P0-based implementation of Hibernate ConnectionProvider
Requires: %{name} = %{version}-%{release}
Requires: c3p0

%description c3p0
%{summary}.

%package proxool
Summary: Proxool-based implementation of Hibernate ConnectionProvder
Requires: %{name} = %{version}-%{release}

%description proxool
%{summary}.

%package ehcache
Summary: Integration of Hibernate with Ehcache
Requires: %{name} = %{version}-%{release}
Requires: ehcache-core

%description ehcache
%{summary}.

%package jbosscache
Summary: Integration of hibernate with jbosscache
Requires: %{name} = %{version}-%{release}
Requires: jbosscache-core

%description jbosscache
%{summary}.

%if 0%{?fedora}
%package infinispan
Summary: Integration of Hibernate with Infinispan
Requires: infinispan

%description infinispan
%{summary}.
%endif

%package testing
Summary: Hibernate JUnit test utilities
Requires: %{name} = %{version}-%{release}
Requires: junit

%description testing
%{summary}.

%prep
%setup -q -n %{oname}-%{namedversion}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%pom_remove_plugin org.jboss.maven.plugins:maven-jdocbook-plugin hibernate-parent
%pom_remove_plugin org.jboss.maven.plugins:maven-jdocbook-style-plugin hibernate-parent
%pom_remove_plugin :gmaven-plugin hibernate-parent
%pom_disable_module hibernate-testsuite
%pom_disable_module hibernate-oscache
%pom_disable_module hibernate-swarmcache
%pom_disable_module hibernate-jdbc3-testing
%pom_disable_module hibernate-jdbc4-testing
%if 0%{?fedora}
%else
%pom_disable_module hibernate-infinispan
%endif

# Remove test deps
for m in envers infinispan entitymanager jbosscache ehcache; do
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
sed -i "s|<!-- <scope>test</scope> TODO fix this -->|<scope>test</scope>|" hibernate-infinispan/pom.xml

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

%pom_xpath_set "pom:project/pom:dependencyManagement/pom:dependencies/pom:dependency[pom:artifactId = 'hibernate-commons-annotations' ]/pom:groupId" org.hibernate.common  hibernate-parent

sed -i "s,59 Temple Place,51 Franklin Street,;s,Suite 330,Fifth Floor,;s,02111-1307,02110-1301," lgpl.txt

%build

# Currently 4 tests fail with this error:
# "Unable to get the default Bean Validation factory"
export jdk16_home=/usr
export LANG=en_US.UTF-8
mvn-rpmbuild \
  -Dmaven.local.depmap.file=%{SOURCE1} \
  -DdisableDistribution=true \
  -Dmaven.test.skip=true \
  package \
  javadoc:aggregate

%install

# POM files:
install -d -m 755 %{buildroot}%{_mavenpomdir}

install -pm 644 hibernate-parent/pom.xml  %{buildroot}%{_mavenpomdir}/JPP-%{name}-parent.pom

%add_maven_depmap JPP-%{name}-parent.pom -v "%{majorversion},%{namedversion}"

# Jar files:
install -d -m 755 %{buildroot}%{_javadir}/%{name}

install -m 644 hibernate-core/target/hibernate-core-%{namedversion}.jar %{buildroot}%{_javadir}/%{name}/hibernate-core.jar
install -pm 644 hibernate-core/pom.xml %{buildroot}%{_mavenpomdir}/JPP.%{name}-hibernate-core.pom

%add_maven_depmap JPP.%{name}-hibernate-core.pom %{name}/hibernate-core.jar -v "%{majorversion},%{namedversion}"

%if 0%{?fedora}
for module in c3p0 ehcache infinispan jbosscache proxool \
%else
for module in c3p0 ehcache jbosscache proxool \
%endif
              entitymanager envers testing; do
    install -m 644 hibernate-${module}/target/hibernate-${module}-%{namedversion}.jar %{buildroot}%{_javadir}/%{name}/hibernate-${module}.jar
    install -pm 644 hibernate-${module}/pom.xml %{buildroot}%{_mavenpomdir}/JPP.%{name}-hibernate-${module}.pom
%add_maven_depmap JPP.%{name}-hibernate-${module}.pom %{name}/hibernate-${module}.jar -f ${module} -v "%{majorversion},%{namedversion}"
done

# Javadoc files:
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -rp target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}
%if 0%{?fedora}
%else
    for jar in core entitymanager envers c3p0 ehcache proxool jbosscache testing; do
        ln -sf hibernate-${jar}.jar %{buildroot}%{_javadir}/%{name}/hibernate-${jar}-%{version}.jar
    done
    for pom in parent; do
      ln -sf JPP-%{name}-${pom}.pom %{buildroot}%{_mavenpomdir}/JPP-%{name}-${pom}-%{version}.pom
    done
    for pom in core entitymanager envers c3p0 ehcache proxool jbosscache testing; do
        ln -sf JPP.%{name}-hibernate-${pom}.pom %{buildroot}%{_mavenpomdir}/JPP.%{name}-hibernate-${pom}-%{version}.pom
    done
%endif

%files
%doc changelog.txt lgpl.txt
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/hibernate-core-%{version}.jar
%{_javadir}/%{name}/hibernate-core-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-core-%{namedversion}.jar
%{_mavenpomdir}/JPP-%{name}-parent-%{version}.pom
%{_mavenpomdir}/JPP-%{name}-parent-%{majorversion}.pom
%{_mavenpomdir}/JPP-%{name}-parent-%{namedversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-core-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-core-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-core-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}

%files javadoc
%doc lgpl.txt
%{_javadocdir}/%{name}

%files entitymanager
%doc lgpl.txt
%{_javadir}/%{name}/hibernate-entitymanager-%{version}.jar
%{_javadir}/%{name}/hibernate-entitymanager-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-entitymanager-%{namedversion}.jar
%{_mavenpomdir}/JPP.%{name}-hibernate-entitymanager-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-entitymanager-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-entitymanager-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}-entitymanager

%files envers
%doc lgpl.txt
%{_javadir}/%{name}/hibernate-envers-%{version}.jar
%{_javadir}/%{name}/hibernate-envers-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-envers-%{namedversion}.jar
%{_mavenpomdir}/JPP.%{name}-hibernate-envers-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-envers-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-envers-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}-envers

%files c3p0
%doc lgpl.txt
%{_javadir}/%{name}/hibernate-c3p0-%{version}.jar
%{_javadir}/%{name}/hibernate-c3p0-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-c3p0-%{namedversion}.jar
%{_mavenpomdir}/JPP.%{name}-hibernate-c3p0-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-c3p0-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-c3p0-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}-c3p0

%files ehcache
%doc lgpl.txt
%{_javadir}/%{name}/hibernate-ehcache-%{version}.jar
%{_javadir}/%{name}/hibernate-ehcache-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-ehcache-%{namedversion}.jar
%{_mavenpomdir}/JPP.%{name}-hibernate-ehcache-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-ehcache-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-ehcache-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}-ehcache

%if 0%{?fedora}
%files infinispan
%doc lgpl.txt
%{_javadir}/%{name}/hibernate-infinispan-%{version}.jar
%{_javadir}/%{name}/hibernate-infinispan-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-infinispan-%{namedversion}.jar
%{_mavenpomdir}/JPP.%{name}-hibernate-infinispan-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-infinispan-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-infinispan-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}-infinispan
%endif

%files proxool
%doc lgpl.txt
%{_javadir}/%{name}/hibernate-proxool-%{version}.jar
%{_javadir}/%{name}/hibernate-proxool-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-proxool-%{namedversion}.jar
%{_mavenpomdir}/JPP.%{name}-hibernate-proxool-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-proxool-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-proxool-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}-proxool

%files jbosscache
%doc lgpl.txt
%{_javadir}/%{name}/hibernate-jbosscache-%{version}.jar
%{_javadir}/%{name}/hibernate-jbosscache-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-jbosscache-%{namedversion}.jar
%{_mavenpomdir}/JPP.%{name}-hibernate-jbosscache-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-jbosscache-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-jbosscache-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}-jbosscache

%files testing
%doc lgpl.txt
%{_javadir}/%{name}/hibernate-testing-%{version}.jar
%{_javadir}/%{name}/hibernate-testing-%{majorversion}.jar
%{_javadir}/%{name}/hibernate-testing-%{namedversion}.jar
%{_mavenpomdir}/JPP.%{name}-hibernate-testing-%{version}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-testing-%{majorversion}.pom
%{_mavenpomdir}/JPP.%{name}-hibernate-testing-%{namedversion}.pom
%{_mavendepmapfragdir}/%{name}-testing

%changelog
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
