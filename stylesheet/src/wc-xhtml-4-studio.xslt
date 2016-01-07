<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:sf="http://www.syntext.com/Extensions/Functions"
                version="1.0">


    <xsl:import href="fonts.xsl"/>
    <xsl:import href="page-sizes.xsl"/>
    <xsl:import href="common.xsl"/>
    <xsl:import href="parameters.xsl"/>
    <xsl:import href="defaultLayout.xsl"/>
    <xsl:import href="workcardEff.xsl"/>
    <xsl:import href="signblock.xsl"/>
    <xsl:import href="workcardHeader.xsl"/>
    <xsl:import href="workcardPrelreq.xsl"/>
    <xsl:import href="steps.xsl"/>

    <!--_________________________________________________________________________-->
    <!--         ************* Warning or Caution*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="div[@class='warning']|div[@class='caution']">
        <fo:list-block keep-together.withinpage="always" keep-with-next.within-page="always"
                       padding-top="6pt" provisional-distance-between-starts=".83in">
            <xsl:if test="preceding-sibling::*=''">
                <xsl:attribute name="padding-top">7mm</xsl:attribute>
            </xsl:if>
            <fo:list-item>
                <fo:list-item-label font-weight="bold" end-indent="label-end()">
                    <fo:block>
                        <fo:inline color="{$genTextColor}">
                            <xsl:choose>
                                <xsl:when test="self::div[@class='warning']">WARNING</xsl:when>
                                <xsl:otherwise>CAUTION</xsl:otherwise>
                            </xsl:choose>
                        </fo:inline>
                        <fo:inline color="{$genTextColor}">:<xsl:text> </xsl:text></fo:inline>
                    </fo:block>
                </fo:list-item-label>
                <fo:list-item-body font-weight="bold" start-indent="body-start()">
                    <xsl:apply-templates/>
                </fo:list-item-body>
            </fo:list-item>
        </fo:list-block>
    </xsl:template>

</xsl:stylesheet>