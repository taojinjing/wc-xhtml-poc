<xsl:stylesheet xmlns:sf="http://www.syntext.com/Extensions/Functions"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:xi="http://www.w3.org/2001/XInclude"
                xmlns:xse="http://www.syntext.com/Extensions/XSLT-1.0"
                extension-element-prefixes="xse sf"
                xmlns:exslt="http://exslt.org/common"
                xmlns:h="http://www.w3.org/1999/xhtml"
                version="1.0">




    <xsl:template match="h:div[@class='tails']">
        <xsl:variable name="cnt" select="count(h:div[@class='airplane-tail'])"/>
        <fo:block border-width="3pt" xsl:use-attribute-sets="space-indent">
            <fo:inline treat-as-word-space="true">
                <fo:inline color="{$genTextColor}" font-weight="bold">EFFECTIVITY: </fo:inline>
                <xsl:for-each select="h:div[@class='airplane-tail']">
                    <fo:inline color="{$lookupTextColor}">
                        <xsl:value-of select="node()"/>
                    </fo:inline>
                    <!--<xsl:apply-templates select="node()"/>-->
                    <xsl:if test="position() != $cnt">, </xsl:if>
                </xsl:for-each>
            </fo:inline>
        </fo:block>
    </xsl:template>
</xsl:stylesheet>