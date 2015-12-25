<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:sf="http://www.syntext.com/Extensions/Functions"
                version="1.0">

    <!--_________________________________________________________________________-->
    <!--         *************Sign*************                                                                                -->
    <!-- Define signature Block, will generate # of Signature Block                                             -->
    <!-- depending on signature blocks in  xml file                                                                    -->
    <xsl:template match="h:div[@class='sign']">
        <xsl:variable name="indent">
            <xsl:variable name="blocks">
                <xsl:value-of select="count(h:div[@class='block'])"/>
            </xsl:variable>
            <xsl:choose>
                <xsl:when test="$blocks &gt; 1 and $blocks &lt; 7">
                    <xsl:value-of select="string(6.95 - number($blocks))"/>
                </xsl:when>
                <xsl:when test="$blocks = 1">
                    <xsl:text>6</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>2.25</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <fo:table padding-top="6pt" start-indent="{concat($indent, 'in')}">
            <xsl:call-template name="indicateChanges"/>
            <xsl:for-each select="h:div[@class='block']">
                <fo:table-column column-width="1.0in"/>
                <fo:table-column column-width="1pt"/>
            </xsl:for-each>
            <fo:table-body>
                <fo:table-row height="18mm" start-indent="0">
                    <xsl:apply-templates select="h:div[@class='block']"/>
                </fo:table-row>
            </fo:table-body>
        </fo:table>
        <xsl:apply-templates select="h:div[@class='eff']|h:div[@class='location']|h:div[@class='sources']"/>
    </xsl:template>

    <xsl:template match="h:div[@class='block']">
        <fo:table-cell border-width="1pt" border-color="black" border-style="solid"
                       text-align="center">
            <fo:table border-width="0pt">
                <fo:table-body border-width="0pt">
                    <xsl:if test="h:div[@class='sign-label']">
                        <fo:table-row height="3mm" border-width="0pt">
                            <fo:table-cell text-align="center" font-size="{$font.size.8pt}"
                                           border-width="0pt">
                                <xsl:apply-templates select="h:div[@class='sign-label']"/>
                            </fo:table-cell>
                        </fo:table-row>
                    </xsl:if>
                    <fo:table-row height="3mm" border-width="0pt">
                        <fo:table-cell border-top-width="1pt" border-bottom-width="1pt"
                                       border-color="black" border-style="solid" font-size="{$font.size.8pt}"
                                       text-align="center">
                            <xsl:apply-templates select="h:div[@class='sign-skill']"/>
                        </fo:table-cell>
                    </fo:table-row>
                </fo:table-body>
            </fo:table>
        </fo:table-cell>
        <fo:table-cell>
            <xsl:text> </xsl:text>
        </fo:table-cell>
    </xsl:template>

    <xsl:template match="h:div[@class='sign-label']|h:div[@class='sign-skill']">
        <fo:inline text-align="center" color="{$lookupTextColor}">
            <xsl:value-of select="text()"/>
        </fo:inline>
    </xsl:template>

</xsl:stylesheet>