<?xml version="1.0"?>
<!--###################################################
# workcardHeader.xsl
# This is Stylsheet for Workcard authoring
######################################################
# Version history
#         20050915   
#  RG  0.01   Written
######################################################-->
<xsl:stylesheet xmlns:sf="http://www.syntext.com/Extensions/Functions"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:xi="http://www.w3.org/2001/XInclude"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                extension-element-prefixes="xse sf"
                xmlns:exslt="http://exslt.org/common"
                xmlns:h="http://www.w3.org/1999/xhtml"
                version="1.0">
    <xsl:template name="header">
      <fo:block font-family="{$sans.font.family}" font-size="{$font.size.10pt}">
        <fo:table>
          <fo:table-column column-width="proportional-column-width(1)"/>
          <fo:table-column column-width="proportional-column-width(1)"/>
          <fo:table-body>
            <fo:table-row>
              <fo:table-cell>
                <fo:block font-weight="bold" color="{$lookupTextColor}">
                  <xsl:copy-of select="h:div[@class='wc-title']/text()"/>
                </fo:block>
              </fo:table-cell>
              <fo:table-cell background-color="#E0E0E0" number-rows-spanned="2" border-start-color="black" border-start-width="1pt" border-start-style="solid" border-end-color="black" border-end-width="1pt" border-end-style="solid" border-before-color="black" border-before-width="1pt" border-before-style="solid" padding="2pt" border-color="black" border-width="1pt">
                <fo:block display-align="before" font-family="{$sans.font.family}" font-size="{$font.size.10pt}">
                <xsl:variable name="majorZone">
                  <xsl:value-of select="h:div[@class='major-zone']"/>
                </xsl:variable>
                <xsl:variable name="carrier">
                  <xsl:value-of select="h:div[@class='carrier-code']"/>
                </xsl:variable>
                <xsl:variable name="mfg">
                  <xsl:value-of select="h:div[@class='mfg']"/>
                </xsl:variable>
                <xsl:variable name="model">
                  <xsl:value-of select="h:div[@class='model']"/>
                </xsl:variable>
                <xsl:variable name="dash">
                  <xsl:value-of select="h:div[@class='dash']"/>
                </xsl:variable>
                <xsl:variable name="zn-desc">
                  <xsl:value-of select="document(concat(sf:server(),
                                        '/getZoneInfo.dox?prgrss=true&amp;zone=',$majorZone,
                                        '&amp;carrier=',$carrier,'&amp;mfg=',
                                        $mfg,'&amp;model=',$model,'&amp;dash=',
                                        $dash,'&amp;sessionid=',sf:session-id()))/zone-description"/>
                </xsl:variable>
                <fo:inline color="{$genTextColor}" font-weight="bold">
                  <xsl:value-of select="$zn-desc"/>
                </fo:inline>
                </fo:block>
              </fo:table-cell>
            </fo:table-row>
            <fo:table-row>
              <fo:table-cell>
                <fo:table table-layout="fixed">
                  <fo:table-column column-width="proportional-column-width(2)"/>
                  <fo:table-column column-width="proportional-column-width(1)"/>
                  <fo:table-body>
                    <fo:table-row>
                      <fo:table-cell  display-align="after" text-align="start">
                        <fo:block padding-top="14mm">
                          <fo:inline color="{$genTextColor}">Card:</fo:inline>
                          <fo:inline font-weight="bold" color="{$lookupTextColor}">
                            <xsl:copy-of select="h:div[@class='wc-num']/text()"/>
                          </fo:inline>
                        </fo:block>
                      </fo:table-cell>
                      <fo:table-cell display-align="after" text-align="end" padding-right="4pt">
                        <fo:block padding-top="14mm">
                          <fo:inline color="{$genTextColor}">Crew:  </fo:inline>
                          <xsl:choose>
                            <xsl:when test="crew-type">
                              <xsl:apply-templates select="h:div[@class='crew-type']" mode="list"/>
                            </xsl:when>
                            <xsl:otherwise>
                              <fo:inline color="{$lookupTextColor}" baseline-shift="-5pt">
                                <xsl:variable name="img" select="concat($style-path,'\images\crew-type.jpg')"/>
                                <fo:external-graphic src="{$img}"/>
                              </fo:inline>
                            </xsl:otherwise>
                          </xsl:choose>
                        </fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                  </fo:table-body>
                </fo:table>
              </fo:table-cell>
            </fo:table-row>
          </fo:table-body>
        </fo:table>
        <fo:table table-layout="fixed">
          <fo:table-body>
            <fo:table-row>
              <fo:table-cell background-color="#E0E0E0" border-start-color="black" padding="4pt" border-style="solid" border-color="black" border-width="1pt">
                <fo:block>
                  <fo:table table-layout="fixed" font-weight="bold">
                    <fo:table-column column-number="1" column-width="15%"/>
				<fo:table-column column-number="2" column-width="5%"/>
				<fo:table-column column-number="3" column-width="60%"/>
				<fo:table-column column-number="4" column-width="20%"/>
                    <fo:table-body>
                      <fo:table-row>
                        <fo:table-cell text-align="left">
                          <fo:block>
                            <xsl:choose>
                              <xsl:when test="carrier-code = 'NWA'">
                                <fo:inline color="{$genTextColor}">Northwest Airlines</fo:inline>
                              </xsl:when>
                              <xsl:otherwise>
                                <xsl:apply-templates select="h:div[@class='carrier-code']" mode="list"/>
                              </xsl:otherwise>
                            </xsl:choose>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell text-align="center" color="{$lookupTextColor}">
                          <fo:block>
                            <xsl:choose>
                              <xsl:when test="model or dash">
                                <xsl:apply-templates select="h:div[@class='model']" mode="list"/>
                                <xsl:text> - </xsl:text>
                                <xsl:apply-templates select="h:div[@class='dash']" mode="list"/>
                              </xsl:when>
                              <xsl:otherwise>
                                <xsl:variable name="img" select="concat($style-path,'\images\model.jpg')"/>
                                <fo:external-graphic src="{$img}"/>
                              </xsl:otherwise>
                            </xsl:choose>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell text-align="center" color="{$lookupTextColor}">
                          <xsl:choose>
                            <xsl:when test="../mainfunc/head-flags/head-flag">
                              <fo:block border-color="black" border-width="1pt">
                              <xsl:variable name="headFlagDefList" select="document(concat(string(sf:server()), '/getDefinitionListAsXml.dox;jsessionid=', string(sf:session-id()), '?definitionList=hflag-def'))"/>
                                <xsl:for-each select="../mainfunc/head-flags//head-flag">
                                	 <xsl:variable name="headFlagValue" select="@type"/>
									 <xsl:value-of select="exslt:node-set($headFlagDefList)//body/row[cell[1]=$headFlagValue]/cell[2]"/>
	                                 <xsl:if test="not(position()=last())">
                                           <xsl:text> / </xsl:text>
                                     </xsl:if>
                                </xsl:for-each> 
                              </fo:block>
                            </xsl:when>
                            <xsl:when test="//xi:include and starts-with(//xi:include/@xpointer, 'W')= true()">
                              <xsl:variable name="targetDocId"><xsl:value-of select="substring-before(//xi:include/@href,'.')"/>.xml</xsl:variable>
                              <xsl:variable name="targetXpointer">
                                <xsl:value-of select="//xi:include/@xpointer"/>
                              </xsl:variable>                              
                              <xsl:if test="starts-with($targetXpointer, 'W')">
                                <xsl:apply-templates select="document($targetDocId,/)//mainfunc[@id=$targetXpointer or @mfid=$targetXpointer]/head-flags" mode="exhead-flags"/>
                              </xsl:if>
                            </xsl:when>
                            <xsl:otherwise>
                              <xsl:text> </xsl:text>
                            </xsl:otherwise>
                          </xsl:choose>
                        </fo:table-cell>
                        <fo:table-cell text-align="right">
                          <xsl:apply-templates select="." mode="wctype-list"/>
                        </fo:table-cell>
                      </fo:table-row>
                    </fo:table-body>
                  </fo:table>
                </fo:block>
              </fo:table-cell>
            </fo:table-row>
          </fo:table-body>
        </fo:table>
      </fo:block>
    </xsl:template>
  
    <xsl:template match="h:div[@class='head-flags']" mode="exhead-flags">
      <fo:block border-color="black" border-width="1pt">
        <xsl:variable name="adfar" select="head-flag[@type='hf01']"/>
        <xsl:variable name="etops" select="head-flag[@type='hf02']"/>
        <xsl:for-each select="head-flag">
          <xsl:if test="position() != 1">
            <xsl:choose>
              <xsl:when test="@type='hf02' and $adfar"/>
              <xsl:otherwise>
                <xsl:text>,</xsl:text>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:if>
          <xsl:choose>
            <xsl:when test="@type='hf01'">
              <xsl:choose>
                <xsl:when test="$etops">
                  <xsl:text>AD/FAR - ETOPS</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:text>AD/FAR</xsl:text>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:when>
            <xsl:when test="@type='hf02'">
              <xsl:if test="$adfar=''">
                <xsl:text>ETOPS</xsl:text>
              </xsl:if>
            </xsl:when>
            <xsl:when test="@type='hf04'">
              <xsl:text>X-RAY</xsl:text>
            </xsl:when>
            <xsl:when test="@type='hf05'">
              <xsl:text>NDT</xsl:text>
            </xsl:when>
            <xsl:when test="@type='hf06'">
              <xsl:text>CORROSION</xsl:text>
            </xsl:when>
            <xsl:when test="@type='hf07'">
              <xsl:text>DINOL</xsl:text>
            </xsl:when>
            <xsl:otherwise>
              [<xsl:value-of select="@type"/>]
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each> 
      </fo:block>
    </xsl:template>

    <xsl:template match="h:div[@class='wctype']|h:div[@class='carrier-code']" mode="list">
      <fo:inline>
        <xsl:choose>
          <xsl:when test="node()">
            <xsl:text>(</xsl:text>
            <xsl:copy-of select="text()"/>
            <xsl:text>)</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates/>
          </xsl:otherwise>
        </xsl:choose>
      </fo:inline>
    </xsl:template>

    <xsl:template match="h:div[@class='crew-type']" mode="list">
      <fo:inline font-weight="bold" color="{$lookupTextColor}">
        <xsl:copy-of select="text()"/> 
      </fo:inline>
    </xsl:template>

    <xsl:template match="h:div[@class='model']|h:div[@class='dash']" mode="list">
      <fo:inline>
        <xsl:copy-of select="text()"/> 
      </fo:inline>
    </xsl:template>

    <xsl:template match="h:div[@class='prelreq']" mode="wctype-list">
      <fo:block color="{$lookupTextColor}">
         <xsl:apply-templates select="h:div[@class='wctype']" mode="list"/>
      </fo:block>
    </xsl:template>

    <xsl:template match="h:div[@class='wctype']" mode="list">
      <fo:block color="{$lookupTextColor}">
        <xsl:choose>
          <xsl:when test="node()">
            <xsl:variable name="wctype">
              <xsl:value-of select="text()"/>
            </xsl:variable>
            <xsl:variable name="wc-type" select="document(concat(sf:server(),
                      '/getWCTypeInfo.dox?prgrss=true&amp;wctype=',$wctype,                                     
                      '&amp;sessionid=',sf:session-id()))/type-description"/>
            <xsl:if test="normalize-space($wc-type/text())=''">
              <xsl:copy-of select="text()"/>
            </xsl:if>
            <xsl:copy-of select="$wc-type/text()"/>
          </xsl:when>
          <xsl:otherwise>			
            <xsl:variable name="img" select="concat($style-path,'\images\wctype.jpg')"/>
            <fo:external-graphic src="{$img}"/>
          </xsl:otherwise>
        </xsl:choose>
      </fo:block>
    </xsl:template>

    <xsl:template match="h:div[@class='estimations']">
        <fo:block border-width="3pt" xsl:use-attribute-sets="space-indent">
            <fo:block>
                <fo:inline color="{$genTextColor}" font-weight="bold">ESTIMATIONS:  </fo:inline>
            </fo:block>
            <fo:table  table-layout="fixed" padding-top="6pt" start-indent="0" border-bottom-width="1px" border-bottom-color="black" border-style="solid">
               <fo:table-column column-width="30mm"/>
               <fo:table-column column-width="15mm"/>
               <fo:table-column column-width="15mm"/>
               <fo:table-column column-width="30mm"/>
               <fo:table-header start-indent="0pt">
                 <fo:table-row height="8mm" start-indent="0">
                     <fo:table-cell text-align="center" color="{$lookupTextColor}" font-weight="bold" border-top-width="1px" border-left-width="1px" border-color="black" border-style="solid">
                         <xsl:text>Trade</xsl:text>
                     </fo:table-cell>
                     <fo:table-cell text-align="center" color="{$lookupTextColor}" font-weight="bold" border-top-width="1px" border-left-width="1px" border-right-width="1px" border-color="black" border-style="solid" >
                         <xsl:text>Staff</xsl:text>
                     </fo:table-cell>
                     <fo:table-cell text-align="center" color="{$lookupTextColor}" font-weight="bold" border-top-width="1px" border-right-width="1px" border-color="black" border-style="solid">
                         <xsl:text>Hours</xsl:text>
                     </fo:table-cell>
                     <fo:table-cell text-align="center" color="{$lookupTextColor}" font-weight="bold" border-top-width="1px" border-right-width="1px" border-color="black" border-style="solid">
                         <xsl:text>Duration</xsl:text>
                     </fo:table-cell>
                 </fo:table-row>
               </fo:table-header>
               <fo:table-body>
                       <xsl:apply-templates select="h:div[@class='estimation']"/>
               </fo:table-body>
            </fo:table>
        </fo:block>
    </xsl:template>

    <xsl:template match="h:div[@class='estimation']">
      <fo:table-row start-indent="0"  height="8mm">
        <fo:table-cell display-align="center" border-top-width="1px" border-left-width="1px" border-color="black" border-style="solid">
            <xsl:value-of select="h:div[@class='skill']"/>
            <xsl:text> </xsl:text>
        </fo:table-cell>
        <fo:table-cell display-align="center" border-top-width="1px" border-left-width="1px" border-right-width="1px" border-color="black" border-style="solid">
            <xsl:value-of select="h:div[@class='staff']"/>
            <xsl:text> </xsl:text>
        </fo:table-cell>
        <fo:table-cell display-align="center" border-top-width="1px" border-right-width="1px" border-color="black" border-style="solid">
            <xsl:value-of select="h:div[@class='effort']"/>
            <xsl:text> </xsl:text>
        </fo:table-cell>
        <fo:table-cell display-align="center" border-top-width="1px" border-right-width="1px" border-color="black" border-style="solid">
            <xsl:value-of select="h:div[@class='duration']"/>
            <xsl:text> </xsl:text>
        </fo:table-cell>
     </fo:table-row>
    </xsl:template>
    
</xsl:stylesheet>
    