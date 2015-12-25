<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:sf="http://www.syntext.com/Extensions/Functions"
                version="1.0">


    <xsl:output method="xml" indent="yes"/>
    <xsl:variable name="pagewidth" select="21.5"/>
    <xsl:variable name="bodywidth" select="19"/>

    <xsl:template match="h:html">
        <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format">

            <fo:layout-master-set>
                <fo:simple-page-master master-name="mainPage"
                                       page-height="27.9cm"
                                       page-width="{$pagewidth}cm"
                                       margin-left="1cm"
                                       margin-right="1cm"
                                       margin-top="1cm"
                                       margin-bottom="1cm">
                    <fo:region-body
                            margin-top="1cm"
                            margin-bottom="1cm" />
                </fo:simple-page-master>

            </fo:layout-master-set>

            <fo:page-sequence master-reference="mainPage" initial-page-number="1">
                <xsl:apply-templates />
            </fo:page-sequence>
        </fo:root>
    </xsl:template>

    <xsl:template match="h:body">
        <fo:flow flow-name="xsl-region-body" font-family="serif"
                 font-size="10pt">
            <xsl:apply-templates/>
        </fo:flow>
    </xsl:template>

    <xsl:template match="h:div">
        <fo:block>
            <xsl:if test="@class='bordered'">
                <xsl:attribute name="border-width">1pt</xsl:attribute>
                <xsl:attribute name="border-style">solid</xsl:attribute>
            </xsl:if>
            <xsl:call-template name="set-alignment"/>
            <xsl:call-template name="set-pagebreak"/>
            <xsl:apply-templates/>
        </fo:block>
    </xsl:template>

    <xsl:template name="set-alignment">
        <xsl:choose>
            <xsl:when test="@align='left' or contains(@class,'left')">
                <xsl:attribute name="text-align">start</xsl:attribute>
            </xsl:when>
            <xsl:when test="@align='center' or contains(@class,'center')">
                <xsl:attribute name="text-align">center</xsl:attribute>
            </xsl:when>
            <xsl:when test="@align='right' or contains(@class,'right')">
                <xsl:attribute name="text-align">end</xsl:attribute>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template name="set-pagebreak">
        <xsl:if test="contains(@style, 'page-break-before')">
            <xsl:attribute name="break-before">page</xsl:attribute>
        </xsl:if>
        <xsl:if test="contains(@style, 'page-break-after')">
            <xsl:attribute name="break-after">page</xsl:attribute>
            <xsl:message><xsl:value-of select="@style"/></xsl:message>
        </xsl:if>
    </xsl:template>

</xsl:stylesheet>