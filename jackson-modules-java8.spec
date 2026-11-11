Name:		jackson-modules-java8
Version:	2.22.3
Release:	2
Summary:	Jackson modules for Java 8 types
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/FasterXML/jackson-modules-java8
Source0:	https://github.com/FasterXML/jackson-modules-java8/archive/refs/tags/jackson-modules-java8-%{version}.tar.gz#/jackson-modules-java8-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-core)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-databind)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-annotations)
BuildRequires:	mvn(ch.randelshofer:fastdoubleparser)

%description
Jackson %{version} modules that read and write Java 8 Optional values
and the java.time API. Gradle 9.9.1 strictly pins both coordinates.
The parameter-names module is not in that pin and is not built here.

%prep
%autosetup -n jackson-modules-java8-jackson-modules-java8-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete
find . -path '*/META-INF/services/*' -type f -exec sed -i 's/\r$//' {} +

%build
sed -e 's/@package@/com.fasterxml.jackson.datatype.jdk8/' \
	-e 's/@projectversion@/%{version}/' \
	-e 's/@projectgroupid@/com.fasterxml.jackson.datatype/' \
	-e 's/@projectartifactid@/jackson-datatype-jdk8/' \
	datatypes/src/main/java/com/fasterxml/jackson/datatype/jdk8/PackageVersion.java.in \
	> datatypes/src/main/java/com/fasterxml/jackson/datatype/jdk8/PackageVersion.java
sed -e 's/@package@/com.fasterxml.jackson.datatype.jsr310/' \
	-e 's/@projectversion@/%{version}/' \
	-e 's/@projectgroupid@/com.fasterxml.jackson.datatype/' \
	-e 's/@projectartifactid@/jackson-datatype-jsr310/' \
	datetime/src/main/java/com/fasterxml/jackson/datatype/jsr310/PackageVersion.java.in \
	> datetime/src/main/java/com/fasterxml/jackson/datatype/jsr310/PackageVersion.java
grep -F -q '%{version}' datatypes/src/main/java/com/fasterxml/jackson/datatype/jdk8/PackageVersion.java
grep -F -q '%{version}' datetime/src/main/java/com/fasterxml/jackson/datatype/jsr310/PackageVersion.java

find datatypes/src/main/java -name '*.java' ! -name 'module-info.java' > jdk8-sources.list
find datetime/src/main/java -name '*.java' ! -name 'module-info.java' > jsr310-sources.list
test "$(wc -l < jdk8-sources.list)" -eq 22
test "$(wc -l < jsr310-sources.list)" -eq 56
CP=%{_javadir}/jackson-core.jar:%{_javadir}/jackson-databind.jar:%{_javadir}/jackson-annotations.jar:%{_javadir}/fastdoubleparser.jar
mkdir -p jdk8-classes jsr310-classes
javac --release 8 -encoding UTF-8 -cp "$CP" -d jdk8-classes @jdk8-sources.list
javac --release 8 -encoding UTF-8 -cp "$CP" -d jsr310-classes @jsr310-sources.list
/bin/cp -a datatypes/src/main/resources/. jdk8-classes/
/bin/cp -a datetime/src/main/resources/. jsr310-classes/
jar cf jackson-datatype-jdk8.jar -C jdk8-classes .
jar cf jackson-datatype-jsr310.jar -C jsr310-classes .
jar tf jackson-datatype-jdk8.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
jar tf jackson-datatype-jsr310.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
javap -verbose -cp jackson-datatype-jdk8.jar com.fasterxml.jackson.datatype.jdk8.Jdk8Module | grep -F 'major version: 52'
javap -verbose -cp jackson-datatype-jsr310.jar com.fasterxml.jackson.datatype.jsr310.JavaTimeModule | grep -F 'major version: 52'

cat > jackson-datatype-jdk8.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.fasterxml.jackson.datatype</groupId>
  <artifactId>jackson-datatype-jdk8</artifactId>
  <version>2.22.3</version>
  <name>Jackson datatype: jdk8</name>
  <description>Jackson support for Java 8 Optional and streams</description>
  <licenses>
    <license>
      <name>Apache-2.0</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.23.0</version>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-core</artifactId>
      <version>2.23.0</version>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-annotations</artifactId>
      <version>2.23</version>
    </dependency>
  </dependencies>
</project>
EOF

cat > jackson-datatype-jsr310.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.fasterxml.jackson.datatype</groupId>
  <artifactId>jackson-datatype-jsr310</artifactId>
  <version>2.22.3</version>
  <name>Jackson datatype: jsr310</name>
  <description>Jackson support for java.time</description>
  <licenses>
    <license>
      <name>Apache-2.0</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.23.0</version>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-core</artifactId>
      <version>2.23.0</version>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-annotations</artifactId>
      <version>2.23</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact jackson-datatype-jdk8.pom:jackson-datatype-jdk8.jar \
	--file-name jackson-datatype-jdk8 \
	--filelist .mfiles-jdk8
sysjar install --buildroot %{buildroot} \
	--artifact jackson-datatype-jsr310.pom:jackson-datatype-jsr310.jar \
	--file-name jackson-datatype-jsr310 \
	--filelist .mfiles-jsr310
awk '!seen[$0]++' .mfiles-jdk8 .mfiles-jsr310 > .mfiles

%check
mkdir -p check
cat > check/Smoke.java << 'END'
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jdk8.Jdk8Module;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import java.time.LocalDate;
import java.util.Optional;
public class Smoke {
	public static void main(String[] args) throws Exception {
		Jdk8Module jdk8 = new Jdk8Module();
		ObjectMapper optMapper = new ObjectMapper().registerModule(jdk8);
		String optJson = optMapper.writeValueAsString(Optional.of("ok"));
		Optional<?> back = optMapper.readValue(optJson,
			optMapper.getTypeFactory().constructParametricType(Optional.class, String.class));
		if (!"ok".equals(back.get())) {
			throw new RuntimeException(optJson);
		}
		JavaTimeModule timeModule = new JavaTimeModule();
		ObjectMapper timeMapper = new ObjectMapper().registerModule(timeModule);
		LocalDate day = LocalDate.of(2020, 1, 2);
		LocalDate read = timeMapper.readValue(timeMapper.writeValueAsString(day), LocalDate.class);
		if (!day.equals(read)) {
			throw new RuntimeException(String.valueOf(read));
		}
		System.out.println("jackson_java8_ok " + jdk8.version() + " " + back.get() + " " + read);
	}
}
END
JDK8=%{buildroot}%{_javadir}/jackson-datatype-jdk8.jar
JSR=%{buildroot}%{_javadir}/jackson-datatype-jsr310.jar
test -f "$JDK8"
test -f "$JSR"
CP="$JDK8:$JSR:%{_javadir}/jackson-core.jar:%{_javadir}/jackson-databind.jar:%{_javadir}/jackson-annotations.jar:%{_javadir}/fastdoubleparser.jar"
javac --release 8 -encoding UTF-8 -cp "$CP" -d check check/Smoke.java
java -cp "check:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'jackson_java8_ok 2.22.3 ok 2020-01-02' check/out.txt

%files -f .mfiles
%doc LICENSE
