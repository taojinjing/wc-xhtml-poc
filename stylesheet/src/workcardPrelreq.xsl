<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                xmlns:sf="http://www.syntext.com/Extensions/Functions"
                extension-element-prefixes="xse sf"
                version="1.0">



    <!-- Define prelreq element -->
    <!--__________________________________________________________________-->
    <!--          ****************Prelreq*******************             -->
    <!--__________________________________________________________________-->
    <xsl:template match="h:div[@class='prelreq']">
        <fo:block>
            <xsl:call-template name="header"/>
            <fo:block padding-top="2mm" font-family="{$sans.font.family}"
                      font-size="{$font.size.10pt}" background-color="#E0E0E0">
                <xsl:apply-templates select="h:div[@class='major-zone']"/>
                <xsl:choose>
                    <xsl:when test="h:div[@class='maintflow-num']">
                        <xsl:apply-templates select="h:div[@class='maintflow-num']"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <fo:block xsl:use-attribute-sets="space-indent">
                            <fo:inline color="{$genTextColor}" font-weight="bold">MAINTFLOW-NUM: </fo:inline>
                            <fo:inline color="{$lookupTextColor}" baseline-shift="-5pt">
                                <xsl:variable name="img" select="concat($style-path,'\images\maintflow-num.jpg')"/>
                                <fo:external-graphic src="{$img}"/>
                            </fo:inline>
                        </fo:block>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'source-docs'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'checks'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'configurations'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'forecasts'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'zones-panels'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'drawings'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'references'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'tools'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'parts'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'circuit-breakers'"/>
                </xsl:call-template>
                <xsl:call-template name="process-elements">
                    <xsl:with-param name="elem" select="'estimations'"/>
                </xsl:call-template>
                <!--<xsl:apply-templates select="*[not(self::major-zone or self::maintflow-num or-->
                <!--self::source-docs or self::checks or self::forecasts or-->
                <!--self::configurations or self::references or self::tools or self::parts or-->
                <!--self::circuit-breakers or self::zones-panels or self::drawings or self::estimations)]"/>-->
            </fo:block>
        </fo:block>
    </xsl:template>

    <xsl:template name="process-elements">
        <xsl:param name="elem" select="''"/>
        <xsl:param name="elem-node" select="h:div[@class=$elem]"/>
        <xsl:choose>
            <xsl:when test="$elem-node">
                <xsl:apply-templates select="$elem-node"/>
            </xsl:when>
            <xsl:otherwise>
                <fo:inline color="{$lookupTextColor}" baseline-shift="-5pt">
                    <xsl:variable name="img" select="concat($style-path,'\images\', $elem, '.jpg')"/>
                    <fo:external-graphic src="{$img}"/>
                </fo:inline>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="h:div[@class='major-zone']">
        <fo:block xsl:use-attribute-sets="space-indent">
            <fo:inline color="{$genTextColor}" font-weight="bold">MAJOR-ZONE: </fo:inline>
            <fo:inline color="{$lookupTextColor}">
                <xsl:value-of select="."/>
            </fo:inline>
        </fo:block>
    </xsl:template>

    <xsl:template match="h:div[@class='maintflow-num']">
        <fo:block xsl:use-attribute-sets="space-indent">
            <fo:inline color="{$genTextColor}" font-weight="bold">MAINTFLOW-NUM: </fo:inline>
            <fo:inline color="{$lookupTextColor}">
                <xsl:value-of select="."/>
            </fo:inline>
        </fo:block>
    </xsl:template>

    <xsl:template match="h:div[@class='carrier-code']|h:div[@class='model']|
            h:div[@class='dash']|h:div[@class='mfg']|
            h:div[@class='wctype']|h:div[@class='wc-num']|
            h:div[@class='wc-title']|h:div[@class='wc-status']|h:div[@class='crew-type']">
    </xsl:template>


    <!--____________________________________________________________________-->
    <!--   Checks, retrieve information from external interfaces             -->
    <!--____________________________________________________________________-->
    <xsl:template match="h:div[@class='checks']">
        <xsl:choose>
            <xsl:when test="h:div[@class='check']">
                <fo:block>
                    <xsl:for-each select="h:div[@class='check']">
                        <fo:block treat-as-word-space="true" xsl:use-attribute-sets="space-indent">
                            <fo:inline color="{$genTextColor}" font-weight="bold">CHECK TYPE: </fo:inline>
                            <fo:inline color="{$lookupTextColor}">
                                <xsl:choose>
                                    <xsl:when test="string-length(h:div[@class='check-type'])=0">
                                        <xsl:text>please select one</xsl:text>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="h:div[@class='check-type']"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </fo:inline>
                        </fo:block>
                        <fo:block>
                            <xsl:choose>
                                <xsl:when test="child::processing-instruction('se:choice')">
                                    <fo:inline color="{$lookupTextColor}">please select one</fo:inline>
                                </xsl:when>
                                <xsl:when test="h:div[@class='effgrp']">
                                    <xsl:apply-templates select="h:div[@class='effgrp']"/>
                                </xsl:when>
                                <xsl:when test="h:div[@class='tails']">
                                    <xsl:apply-templates select="h:div[@class='tails']" mode="check"/>
                                </xsl:when>
                            </xsl:choose>
                        </fo:block>
                    </xsl:for-each>
                </fo:block>
            </xsl:when>
            <xsl:otherwise>
                <fo:inline color="{$genTextColor}" font-weight="bold" xsl:use-attribute-sets="space-indent">FREQUENCY: </fo:inline>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="h:div[@class='tails']" mode="check">
        <xsl:variable name="cnt" select="count(h:div[@class='airplane-tail'])"/>
        <fo:block border-width="3pt" xsl:use-attribute-sets="space-indent">
            <fo:inline treat-as-word-space="true">
                <fo:inline color="{$genTextColor}" font-weight="bold">AIRPLANE TAILS: </fo:inline>
                <fo:inline color="{$lookupTextColor}">
                    <xsl:for-each select="h:div[@class='airplane-tail']">
                        <xsl:choose>
                            <xsl:when test="position() != $cnt">
                                <xsl:value-of select="concat(string(.), ', ')"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="."/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </fo:inline>
            </fo:inline>
        </fo:block>
    </xsl:template>
    <!--____________________________________________________________________-->
    <!--          Forecast                   -->
    <!--____________________________________________________________________-->
    <xsl:template match="h:div[@class='forecasts']">
        <xsl:param name="indent" select="'0'"/>
        <fo:block border-width="3pt" xsl:use-attribute-sets="space-indent">
            <fo:inline font-weight="bold" color="{$genTextColor}">FORECAST:</fo:inline>
            <fo:table table-layout="fixed">
                <fo:table-column column-width="proportional-column-width(1)"/>
                <fo:table-column column-width="proportional-column-width(2)"/>
                <fo:table-column column-width="proportional-column-width(3)"/>
                <fo:table-body>
                    <fo:table-row text-decoration="underline">
                        <fo:table-cell>
                            <fo:block color="{$genTextColor}">Forecast Number</fo:block>
                        </fo:table-cell>
                        <fo:table-cell>
                            <fo:block color="{$genTextColor}">NHA Position</fo:block>
                        </fo:table-cell>
                    </fo:table-row>
                    <xsl:apply-templates/>
                </fo:table-body>
            </fo:table>
        </fo:block>
    </xsl:template>
    <xsl:template match="h:div[@class='forecast']">
        <fo:table-row>
            <xsl:apply-templates/>
        </fo:table-row>
    </xsl:template>
    <xsl:template match="h:div[@class='fc-num']|h:div[@class='nha-pos']">
        <fo:table-cell>
            <fo:block color="{$lookupTextColor}">
                <xsl:value-of select="."/>
            </fo:block>
        </fo:table-cell>
    </xsl:template>


    <!--___________________________________________________________________-->
    <!-- Source-docs, retrieve information from external interfaces        -->
    <!--___________________________________________________________________-->
    <xsl:template match="h:div[@class='source-docs']">
        <fo:block border-width="3pt" xsl:use-attribute-sets="space-indent">
            <fo:inline treat-as-word-space="true">
                <xsl:apply-templates mode="inline"/>
            </fo:inline>
            <xsl:if test="*[not(self::processing-instruction('se:choice'))]">
                <xsl:apply-templates mode="table"/>
            </xsl:if>
        </fo:block>
    </xsl:template>

    <xsl:template match="h:div[@class='eng-proj']"/>
    <xsl:template match="h:div[@class='eng-proj']" mode="inline"/>
    <xsl:template match="h:div[@class='eng-proj']" mode="table"/>
    <xsl:template match="h:div[@class='section-num']" mode="inline"/>
    <xsl:template match="h:div[@class='section-num']" mode="table"/>
    <xsl:template match="h:div[@class='eng-proj-num']" mode="inline"/>
    <xsl:template match="h:div[@class='tasks']" mode="table"/>
    <xsl:template match="h:div[@class='eng-proj-num']"/>
    <xsl:template match="h:div[@class='tasks']" mode="inline">
        <xsl:variable name="cnt" select="count(h:div[@class='task-key'])"/>
        <fo:block color="{$genTextColor}" font-weight="bold">TASK(S): </fo:block>
        <xsl:for-each select="h:div[@class='task-key']">
            <fo:inline color="{$lookupTextColor}">
                <xsl:copy-of select="text()"/>
                <xsl:if test="position() != $cnt">, </xsl:if>
            </fo:inline>
        </xsl:for-each>
    </xsl:template>

    <!--___________________________________________________________________-->
    <!--    TODO:  Configurations             -->
    <!--___________________________________________________________________-->
    <xsl:template match="h:div[@class='configurations']">
        <xsl:variable name="configs">
            <xsl:variable name="taskkey">
                <xsl:value-of select="/workcard/prelreq/source-docs/tasks/task-key"/>
            </xsl:variable>
            <xsl:variable name="carrier">
                <xsl:value-of select="/workcard/prelreq/carrier-code"/>
            </xsl:variable>
            <xsl:variable name="mfg">
                <xsl:value-of select="/workcard/prelreq/mfg"/>
            </xsl:variable>
            <xsl:variable name="model">
                <xsl:value-of select="/workcard/prelreq/model"/>
            </xsl:variable>
            <xsl:variable name="dash">
                <xsl:value-of select="/workcard/prelreq/dash"/>
            </xsl:variable>
            <xsl:copy-of select="document(concat(sf:server(),
                    '/getTaskConfigurations.dox?prgrss=true&amp;taskkey=',$taskkey,
                    '&amp;carriercode=',$carrier,'&amp;mfg=',
                    $mfg,'&amp;model=',$model,'&amp;dash=',
                    $dash,'&amp;sessionid=',sf:session-id()))/configurations" xse:document-mode="ignore-errors"/>
        </xsl:variable>
        <xsl:for-each select="accfg">
            <fo:block xsl:use-attribute-sets="space-indent" border-width="3pt">
                <fo:inline>
                    <xsl:variable name="type" select="accfg-type"/>
                    <xsl:variable name="desc" select="$configs//accfg[string(accfg-type)=string($type)]/accfg-desc"/>
                    <xsl:choose>
                        <xsl:when test="not($desc='')">
                            <fo:block space-before="6pt" space-before.conditionality="retain">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold"><xsl:value-of select="$desc"/>?: </fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='ELECT' or accfg-type='ELEC'">
                            <fo:block space-before="6pt" space-before.conditionality="retain">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">ELECTRICAL POWER REQUIRED? </fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='HYD'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">HYDRAULIC POWER REQUIRED? </fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='ECAM'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">ELECTRONIC CENTRALIZED AIRCRAFT MONITORING REQUIRED?&#160; </fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='ENGRUN'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">ENGINE RUN REQUIRED?&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='FHCNT'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">FLIGHT CONTROL POSITION/MOVEMENT REQUIRED?&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='FUEL'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">FUEL REQUIREMENTS?&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='JACK'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">JACKING/SHORING REQUIREMENTS REQUIRED?&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='MCDU'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">MULTIPURPOSE CONTROL DISPLAY UNIT REQUIRED?&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='PNEU'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">PNEUMATIC PRESSURE REQUIRED?&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='SAFETY'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">SAFETY DEVICES REQUIRED?&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='STANDS'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">STANDS/LIFTS REQUIRED?&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='WASTE'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">WASTE:&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:when test="accfg-type='WATER'">
                            <fo:block space-before="6pt" space-before.conditionality="discard">
                                <fo:inline color="{$genTextColor}">
                                    <fo:inline font-weight="bold">WATER:&#160;</fo:inline>
                                    <xsl:apply-templates select="accfg-state"/>
                                </fo:inline>
                            </fo:block>
                        </xsl:when>
                        <xsl:otherwise>
                            <fo:inline color="{$genTextColor}">
                                <fo:inline font-weight="bold"><xsl:value-of select="accfg-type"/>?: </fo:inline>
                                <xsl:apply-templates select="accfg-state"/>
                            </fo:inline>
                        </xsl:otherwise>
                    </xsl:choose>
                </fo:inline>
                <xsl:text> </xsl:text>
                <xsl:apply-templates select="eff/*"/>
                <xsl:if test="not(eff)">
                    <fo:inline  baseline-shift="-5pt">
                        <xsl:variable name="img" select="concat($style-path,'\images\eff.jpg')"/>
                        <fo:external-graphic src="{$img}"/>
                    </fo:inline>
                </xsl:if>
            </fo:block>
        </xsl:for-each>
    </xsl:template>

    <!-- TODO: accfg-state -->
    <xsl:template match="accfg-state">
        <fo:inline color="{$lookupTextColor}">
            <xsl:choose>
                <xsl:when test=".='Y'">Required</xsl:when>
                <xsl:when test=".='N'">Not Permitted</xsl:when>
                <xsl:when test=".='B'">No Preference</xsl:when>
                <xsl:when test=".='T'">Limited Use</xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="."/>
                </xsl:otherwise>
            </xsl:choose>
        </fo:inline>
    </xsl:template>


    <!--___________________________________________________________________-->
    <!--          References             -->
    <!--__________________________________________________________________-->
    <xsl:template name="db-request">
        <xsl:value-of select="concat(sf:server(), '/getTaskReferencesByRef.dox?')"/>
        <xsl:text>prgrss=true&amp;taskref=</xsl:text>
        <xsl:for-each select="h:div[@class='reference']">
            <xsl:value-of select="string(h:div[@class='source-key'])"/>
            <xsl:text>:</xsl:text>
            <xsl:value-of select="string(h:div[@class='refid'])"/>
            <xsl:if test="not(position() = last())">, </xsl:if>
        </xsl:for-each>
        <xsl:text>&amp;sessionid=</xsl:text>
        <xsl:value-of select="sf:session-id()"/>
    </xsl:template>

    <xsl:template match="h:div[@class='references']">
        <xsl:param name="indent" select="'0'"/>
        <fo:block border-width="3pt">
            <xsl:variable name="request">
                <xsl:call-template name="db-request"/>
            </xsl:variable>
            <!--xsl:message> <xsl:value-of select="$request"/> </xsl:message-->
            <xsl:variable name="doc" select="document($request)" xse:document-mode="ignore-errors"/>
            <fo:block xsl:use-attribute-sets="space-indent">
                <fo:inline font-weight="bold" color="{$genTextColor}">REFERENCES:</fo:inline>
            </fo:block>
            <fo:table table-layout="fixed">
                <fo:table-column column-width="proportional-column-width(1.2)"/>
                <fo:table-column column-width="proportional-column-width(1.4)"/>
                <fo:table-column column-width="proportional-column-width(1.2)"/>
                <fo:table-column column-width="proportional-column-width(1)"/>
                <!-- Add for SD-383 start -->
                <fo:table-column column-width="proportional-column-width(1)"/>
                <!-- Add for SD-383 end -->
                <fo:table-header start-indent="0" color="{$genTextColor}">
                    <fo:table-row>
                        <xsl:for-each select="$table-header/column">
                            <fo:table-cell>
                                <xsl:call-template name="copy-fo-attributes">
                                    <xsl:with-param name="attributes" select="@*"/>
                                </xsl:call-template>
                                <fo:inline text-decoration="underline">
                                    <xsl:value-of select="string()"/>
                                </fo:inline>
                            </fo:table-cell>
                        </xsl:for-each>
                        <!-- Add for SD-383 start -->
                        <fo:table-cell>
                            <fo:block color="{$genTextColor}">Effectivity</fo:block>
                        </fo:table-cell>
                        <!-- Add for SD-383 end -->
                    </fo:table-row>
                </fo:table-header>
                <fo:table-body>
                    <xsl:apply-templates select="h:div[@class='reference']">
                        <xsl:with-param name="ref-data" select="$doc"/>
                    </xsl:apply-templates>
                </fo:table-body>
            </fo:table>
        </fo:block>
    </xsl:template>
    <!--___________________________________________________________________-->
    <!--         ************* Reference*************             -->
    <!--___________________________________________________________________-->
    <xsl:template match="h:div[@class='reference']">
        <xsl:param name="ref-data"/>
        <xsl:variable name="source-key" select="string(h:div[@class='source-key'])"/>
        <xsl:variable name="refid" select="string(h:div[@class='refid'])"/>
        <xsl:variable name="additional" select="$ref-data/references/task[@key=$source-key]/reference[@refid=$refid]"/>
        <fo:table-row>
            <xsl:choose>
                <xsl:when test="$additional/*">
                    <xsl:for-each select="$table-header/column[@name]">
                        <xsl:variable name="column" select="."/>
                        <xsl:variable name="nm" select="string(@name)"/>
                        <xsl:for-each select="$additional/*[local-name()=$nm]">
                            <xsl:call-template name="reference-cell">
                                <xsl:with-param name="column" select="$column"/>
                            </xsl:call-template>
                        </xsl:for-each>
                    </xsl:for-each>

                    <!-- Add for SD-383 start -->
                    <xsl:apply-templates select="h:div[@class='eff']" mode="refereces"/>
                    <xsl:if test="not(h:div[@class='eff'])">
                        <fo:table-cell>
                            <xsl:variable name="img" select="concat($style-path,'\images\eff.jpg')"/>
                            <fo:external-graphic src="{$img}"/>
                        </fo:table-cell>
                    </xsl:if>
                    <!-- Add for SD-383 end -->
                </xsl:when>
                <xsl:otherwise>
                    <fo:table-cell color="{$lookupTextColor}">
                        <fo:inline>
                            <xsl:value-of select="h:div[@class='reforigin-type']"/>
                        </fo:inline>
                    </fo:table-cell>
                    <fo:table-cell color="{$lookupTextColor}">
                        <fo:inline>
                            <xsl:value-of select="h:div[@class='ref-desc']"/>
                        </fo:inline>
                    </fo:table-cell>
                </xsl:otherwise>
            </xsl:choose>
        </fo:table-row>
    </xsl:template>
    <xsl:template name="reference-cell">
        <xsl:param name="column"/>
        <fo:table-cell color="{$lookupTextColor}">
            <xsl:call-template name="copy-fo-attributes">
                <xsl:with-param name="attributes" select="$column/@*"/>
            </xsl:call-template>
            <fo:inline>
                <xsl:value-of select="."/>
            </fo:inline>
        </fo:table-cell>
    </xsl:template>
    <xsl:template name="copy-fo-attributes">
        <xsl:param name="attributes"/>
        <xsl:for-each select="$attributes[substring(local-name(), 1, 3)='fo-']">
            <xsl:attribute name="{substring(name(), 4)}"><xsl:value-of select="string()"/></xsl:attribute>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="h:div[@class='eff']" mode="refereces">
        <fo:table-cell>
            <fo:block color="{$lookupTextColor}">
                <xsl:apply-templates select="node()" mode="simple"/>
            </fo:block>
        </fo:table-cell>
    </xsl:template>
</xsl:stylesheet>