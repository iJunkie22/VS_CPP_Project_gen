# coding=utf-8
__author__ = 'ethan'

import hashlib
import datetime
from sys import platform
import os
import os.path
import fnmatch
import sys
import StringIO


def generate_uid():
    t_stamp = str(datetime.datetime.now())
    r = hashlib.sha256(t_stamp).hexdigest()[0:32]
    uid_str = "{" + r[0:8] + "-" + r[8:12] + "-" + r[12:16] + "-" + r[16:20] + "-" + r[20:32] + "}"
    return uid_str


class Project:
    def __init__(self, proj_path):
        self.globals_guid = generate_uid()
        self.source_guid = generate_uid()
        self.header_guid = generate_uid()
        self.resource_guid = generate_uid()
        self.project_guid = generate_uid()
        self.project_path = str(proj_path)
        if platform == "win32":
            self.path_sep = "\\"
        else:
            self.path_sep = "/"
        self.slashless_pp = self.project_path.rstrip(self.path_sep)
        self.project_folder = self.slashless_pp.rpartition(self.path_sep)[2]
        self.vs_proj_subdir = os.path.join(self.slashless_pp, self.project_folder)
        self.clion_idea_subdir = os.path.join(self.vs_proj_subdir, ".idea")
        cpp_files = None
        self.cpp_files = []
        self.h_files = []

        try:
            results_list = os.listdir(self.vs_proj_subdir)
            self.cpp_files.extend(fnmatch.filter(results_list, "*.cpp"))
            self.h_files.extend(fnmatch.filter(results_list, "*.h"))

        except OSError, e:
            # The project directory does not exist
            os.makedirs(self.vs_proj_subdir)

        finally:
            if len(self.cpp_files) > 0:
                self.cpp_exists = True
            else:
                self.cpp_files = ['main.cpp']
                self.cpp_exists = False

    def template_filters(self):
        new_template = FileTemplate(fp=self.vs_proj_subdir, fn=str(self.project_folder + ".vcxproj.filters"))
        xml_buf = StringIO.StringIO()
        xml_buf.write(u"  <ItemGroup>\n")
        for c_f in self.cpp_files:
            xml_buf.write(u"    <ClCompile Include=\"{0}\">\n".format(c_f))
            xml_buf.write(u"      <Filter>Source Files</Filter>\n")
            xml_buf.write(u"    </ClCompile>\n")
        xml_buf.write(u"  </ItemGroup>\n")
        xml_buf.write(u"  <ItemGroup>\n")
        for h_f in self.h_files:
            xml_buf.write(u"    <ClInclude Include=\"{0}\">\n".format(h_f))
            xml_buf.write(u"      <Filter>Header Files</Filter>\n")
            xml_buf.write(u"    </ClInclude>\n")
        xml_buf.write(u"  </ItemGroup>")
        xml_u_str = xml_buf.getvalue()
        xml_buf.close()

        new_template.format_str = u"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <Filter Include="Source Files">
      <UniqueIdentifier>{source_uid}</UniqueIdentifier>
      <Extensions>cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx</Extensions>
    </Filter>
    <Filter Include="Header Files">
      <UniqueIdentifier>{header_uid}</UniqueIdentifier>
      <Extensions>h;hpp;hxx;hm;inl;inc;xsd</Extensions>
    </Filter>
    <Filter Include="Resource Files">
      <UniqueIdentifier>{resource_uid}</UniqueIdentifier>
      <Extensions>rc;ico;cur;bmp;dlg;rc2;rct;bin;rgs;gif;jpg;jpeg;jpe;resx;tiff;tif;png;wav;mfcribbon-ms</Extensions>
    </Filter>
  </ItemGroup>
{item_groups}
</Project>"""
        new_template.format_dict = dict(source_uid=self.source_guid, header_uid=self.header_guid,
                                        resource_uid=self.resource_guid, item_groups=xml_u_str)
        new_template.write_self()
        return new_template

    def template_sln(self):
        new_template = FileTemplate(fp=self.slashless_pp, fn=str(self.project_folder + ".sln"))
        new_template.format_str = u"""
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio 2012
Project("{project_uid}") = "{proj_name}", "{proj_name}\{proj_name}.vcxproj", "{globals_uid}"
EndProject
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
        Debug|Win32 = Debug|Win32
        Release|Win32 = Release|Win32
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
        {globals_uid}.Debug|Win32.ActiveCfg = Debug|Win32
        {globals_uid}.Debug|Win32.Build.0 = Debug|Win32
        {globals_uid}.Release|Win32.ActiveCfg = Release|Win32
        {globals_uid}.Release|Win32.Build.0 = Release|Win32
    EndGlobalSection
    GlobalSection(SolutionProperties) = preSolution
        HideSolutionNode = FALSE
    EndGlobalSection
EndGlobal
"""
        new_template.format_dict = dict(project_uid=self.project_guid, globals_uid=self.globals_guid, proj_name=self.project_folder)
        new_template.write_self()
        return new_template

    def template_cmake_list(self):
        new_template = FileTemplate(fp=self.vs_proj_subdir, fn="CMakeLists.txt")
        xml_buf = StringIO.StringIO()
        for i, f in enumerate(self.cpp_files, start=1):
            if i != len(self.cpp_files):
                xml_buf.write(u"{0}\n".format(f))
            else:
                xml_buf.write(u"{0}".format(f))
        xml_u_str = xml_buf.getvalue()
        xml_buf.close()

        new_template.format_str = u"""cmake_minimum_required(VERSION 2.8.4)
project({proj_name})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES {cpp_files})
add_executable({proj_name} ${SOURCE_FILES})
"""
        new_template.format_dict = dict(proj_name=self.project_folder, cpp_files=xml_u_str,
                                        CMAKE_CXX_FLAGS=u"{CMAKE_CXX_FLAGS}", SOURCE_FILES=u"{SOURCE_FILES}")
        new_template.write_self()
        return new_template

    def template_vcxproj(self):
        new_template = FileTemplate(fp=self.vs_proj_subdir, fn=str(self.project_folder + ".vcxproj"))
        xml_buf = StringIO.StringIO()
        xml_buf.write(u"  <ItemGroup>\n")
        for c_f in self.cpp_files:
            xml_buf.write(u"    <ClCompile Include=\"{0}\" />\n".format(c_f))
        xml_buf.write(u"  </ItemGroup>\n")
        xml_buf.write(u"  <ItemGroup>\n")
        for h_f in self.h_files:
            xml_buf.write(u"    <ClInclude Include=\"{0}\" />\n".format(h_f))
        xml_buf.write(u"  </ItemGroup>")
        xml_u_str = xml_buf.getvalue()
        xml_buf.close()
        new_template.format_str = u"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|Win32">
      <Configuration>Debug</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|Win32">
      <Configuration>Release</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <PropertyGroup Label="Globals">
    <ProjectGuid>{globals_uid}</ProjectGuid>
    <Keyword>Win32Proj</Keyword>
    <RootNamespace>{proj_name}</RootNamespace>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>v110</PlatformToolset>
    <CharacterSet>Unicode</CharacterSet>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>false</UseDebugLibraries>
    <PlatformToolset>v110</PlatformToolset>
    <WholeProgramOptimization>true</WholeProgramOptimization>
    <CharacterSet>Unicode</CharacterSet>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
  <ImportGroup Label="ExtensionSettings">
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <LinkIncremental>true</LinkIncremental>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <LinkIncremental>false</LinkIncremental>
  </PropertyGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <ClCompile>
      <PrecompiledHeader>
      </PrecompiledHeader>
      <WarningLevel>Level3</WarningLevel>
      <Optimization>Disabled</Optimization>
      <PreprocessorDefinitions>WIN32;_DEBUG;_CONSOLE;%(PreprocessorDefinitions)</PreprocessorDefinitions>
    </ClCompile>
    <Link>
      <SubSystem>Console</SubSystem>
      <GenerateDebugInformation>true</GenerateDebugInformation>
    </Link>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <ClCompile>
      <WarningLevel>Level3</WarningLevel>
      <PrecompiledHeader>
      </PrecompiledHeader>
      <Optimization>MaxSpeed</Optimization>
      <FunctionLevelLinking>true</FunctionLevelLinking>
      <IntrinsicFunctions>true</IntrinsicFunctions>
      <PreprocessorDefinitions>WIN32;NDEBUG;_CONSOLE;%(PreprocessorDefinitions)</PreprocessorDefinitions>
    </ClCompile>
    <Link>
      <SubSystem>Console</SubSystem>
      <GenerateDebugInformation>true</GenerateDebugInformation>
      <EnableCOMDATFolding>true</EnableCOMDATFolding>
      <OptimizeReferences>true</OptimizeReferences>
    </Link>
  </ItemDefinitionGroup>
{item_groups}
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
  <ImportGroup Label="ExtensionTargets">
  </ImportGroup>
</Project>"""
        new_template.format_dict = dict(globals_uid=self.globals_guid, proj_name=self.project_folder, item_groups=xml_u_str)
        new_template.write_self()
        return new_template

    def template_cpp(self):
        new_template = FileTemplate(fp=self.vs_proj_subdir, fn="main.cpp")
        date_today = datetime.datetime.today()
        date_str = str(date_today.strftime("%m/%d/%y"))
        new_template.format_str = u"""/*
*	Program Name: {proj_name}
*
*	Description:
*
*	Inputs:
*
*	Outputs:
*
*	Author: AUTHORNAME
*
*	Date: {date_str}
*
*	Modification History:
*
*/

#include <iostream>
using namespace std;
{program}
"""
        cpp_str2 = u"""
int main( int argc, char * argv[] )
{
    cout << "Hello, World!";

    return 0;
}
"""
        new_template.format_dict = dict(proj_name=self.project_folder, date_str=date_str, program=cpp_str2)
        new_template.write_self()
        return new_template

    def template_clion_name(self):
        new_template = FileTemplate(fp=self.clion_idea_subdir, fn=".name")
        new_template.contents = self.project_folder
        return new_template

    def template_clion_project_iml(self):
        new_template = FileTemplate(fp=self.clion_idea_subdir, fn=str(self.project_folder + ".iml"))
        new_template.contents = u"""<?xml version="1.0" encoding="UTF-8"?>
<module type="CPP_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$" />
    <orderEntry type="inheritedJdk" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
</module>"""
        return new_template

    def template_clion_modules(self):
        new_template = FileTemplate(fp=self.clion_idea_subdir, fn="modules.xml")
        new_template.format_str = u"""<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/{proj_name}.iml" filepath="$PROJECT_DIR$/.idea/{proj_name}.iml" />
    </modules>
  </component>
</project>"""
        new_template.format_dict = dict(proj_name=self.project_folder)
        new_template.write_self()
        return new_template

    def template_clion_misc(self):
        new_template = FileTemplate(fp=self.clion_idea_subdir, fn="misc.xml")
        new_template.contents = u"""<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="CMakeWorkspace" PROJECT_DIR="$PROJECT_DIR$" />
  <component name="ProjectLevelVcsManager" settingsEditedManually="false">
    <OptionsSetting value="true" id="Add" />
    <OptionsSetting value="true" id="Remove" />
    <OptionsSetting value="true" id="Checkout" />
    <OptionsSetting value="true" id="Update" />
    <OptionsSetting value="true" id="Status" />
    <OptionsSetting value="true" id="Edit" />
    <ConfirmationsSetting value="0" id="Add" />
    <ConfirmationsSetting value="0" id="Remove" />
  </component>
  <component name="ProjectRootManager" version="2" />
</project>"""
        return new_template

    def make_folders(self):
        try:
            os.mkdir(os.path.join(self.slashless_pp, "Debug"))
        except OSError:
            pass
        try:
            os.mkdir(os.path.join(self.vs_proj_subdir, ".idea"))
        except OSError:
            pass

    def gen_files(self):
        self.template_sln().write_file()
        self.template_vcxproj().write_file()
        self.template_filters().write_file()
        self.template_clion_modules().write_file()
        self.template_clion_misc().write_file()
        self.template_clion_name().write_file()
        self.template_clion_project_iml().write_file()
        self.template_cmake_list().write_file()

    def main(self):
        try:
            os.makedirs(self.vs_proj_subdir)
        except OSError:
            pass
        self.make_folders()
        self.gen_files()

        if self.cpp_exists is False:
            self.template_cpp().write_file()


class FileTemplate:
    def __init__(self, fp=None, content=None, fn=None):
        self.f_path = fp
        self.contents = content
        self.format_str = str()
        self.format_dict = dict()
        self.f_name = fn

    def write_self(self):
        output = self.format_str.format(**self.format_dict)
        self.contents = output

    def write_file(self):
        template_full_path = os.path.join(self.f_path, self.f_name)
        template_file = open(template_full_path, "w")
        try:
            template_file.write(self.contents)
        finally:
            template_file.close()

if len(sys.argv) > 1:
    infile = str(sys.argv[-1])
    Project(infile).main()
