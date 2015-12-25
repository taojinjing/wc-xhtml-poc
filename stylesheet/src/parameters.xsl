<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:sf="http://www.syntext.com/Extensions/Functions"
                version="1.0">

    <!--from original plug-in start-->
    <xsl:strip-space elements="*"/>
    <xsl:preserve-space elements="type ref"/>

    <xsl:param name="root" select="/"/>

    <!-- Page parameters -->
    <xsl:param name="paper.type" select="'A4'"/>
    <xsl:param name="page.orientation" select="'portrait'"/>
    <xsl:param name="page.margin.bottom" select="'5mm'"/>
    <xsl:param name="page.max.width" select="$page.width"/>
    <xsl:param name="page.margin.inner">5mm</xsl:param>
    <xsl:param name="page.margin.outer">5mm</xsl:param>
    <xsl:param name="page.margin.top" select="'5mm'"/>
    <xsl:param name="body.margin.bottom" select="'5mm'"/>
    <xsl:param name="body.margin.top" select="'5mm'"/>
    <xsl:param name="page.margin.left">5mm</xsl:param>
    <xsl:param name="page.margin.right">5mm</xsl:param>
    <!-- Font parameters -->
    <xsl:param name="body.font.size" select="concat($body.font.master,'pt')"/>
    <xsl:param name="font.size.8pt" select="concat(0.67 * $body.font.master,'pt')"/>
    <xsl:param name="font.size.10pt" select="concat(0.84 * $body.font.master,'pt')"/>
    <xsl:param name="font.size.11pt" select="concat(0.92 * $body.font.master,'pt')"/>
    <xsl:param name="font.size.12pt" select="concat($body.font.master,'pt')"/>
    <xsl:param name="font.size.14pt" select="concat(1.17 * $body.font.master,'pt')"/>
    <xsl:param name="font.size.18pt" select="concat(1.5 * $body.font.master,'pt')"/>
    <xsl:param name="attribute.font.size" select="$font.size.10pt"/>
    <xsl:param name="show.preamble.editing" select="''"/>
    <!-- Other parameters -->
    <!--TODO: update plug-in to get current path -->
    <!--<xsl:param name="style-path" select="sf:style-path()"/>-->
    <xsl:param name="style-path">D:\workspace\wc-xhtml-poc\wc-xhtml-poc\stylesheet\src</xsl:param>
    <xsl:variable name="default.indent.shift" select="'20'"/>
    <xsl:attribute-set name="root">
        <xsl:attribute name="font-family">
            <xsl:value-of select="$body.font.family"/>
        </xsl:attribute>
        <xsl:attribute name="font-size">
            <xsl:value-of select="$body.font.size"/>
        </xsl:attribute>
    </xsl:attribute-set>
    <xsl:attribute-set name="inline.charseq.properties">
        <xsl:attribute name="border-left-width">0pt</xsl:attribute>
        <xsl:attribute name="border-right-width">0pt</xsl:attribute>
    </xsl:attribute-set>
    <xsl:attribute-set name="em">
        <xsl:attribute name="font-weight">bold</xsl:attribute>
    </xsl:attribute-set>
    <xsl:attribute-set name="space-indent">
        <xsl:attribute name="padding-top">6pt</xsl:attribute>
        <!--xsl:attribute name="start-indent">0pt</xsl:attribute-->
        <xsl:attribute name="font-size">
            <xsl:value-of select="$font.size.10pt"/>
        </xsl:attribute>
    </xsl:attribute-set>
    <xsl:param name="document-id"/>


    <xsl:variable name="endSignOff" select="'test'"/>
    <xsl:variable name="lower">abcdefghijklmnopqrstuvwxyz</xsl:variable>
    <xsl:variable name="upper">ABCDEFGHIJKLMNOPQRSTUVWXYZ</xsl:variable>
    <xsl:variable name="table-header">
        <column name="reforigin-type">Origin</column>
        <column name="ref-desc">Description</column>
        <column name="task-primary" fo-text-align="center">Task Primary</column>
        <column name="wc-primary" fo-text-align="center">Workcard Primary</column>
    </xsl:variable>
    <xsl:variable name="panel-table-header">
        <pt1>
            <col>Open</col>
            <col>Close</col>
        </pt1>
        <pt2>
            <col>Open</col>
        </pt2>
        <pt3>
            <col>Close</col>
        </pt3>
        <pt4>
            <col>Open</col>
            <col>Check Cond</col>
        </pt4>
        <pt5>
            <col>Open</col>
            <col>Check Cond</col>
            <col>Protect</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Seal</col>
        </pt5>
        <pt6>
            <col>Check Cond</col>
            <col>Protect</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Seal</col>
        </pt6>
        <pt7>
            <col>Protect</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Seal</col>
            <col>Insp</col>
        </pt7>
        <pt8>
            <col>Protect</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Seal</col>
        </pt8>
        <pt9>
            <col>Open</col>
            <col>Check Cond</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Inspect</col>
            <col>Leak Check</col>
        </pt9>
        <pt10>
            <col>Check Cond</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Inspect</col>
            <col>Leak Check</col>
        </pt10>
        <pt11>
            <col>Initial Res. Ck.</col>
            <col>Open</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Final Res. Ck.</col>
        </pt11>
        <pt12>
            <col>Initial Res. Ck.</col>
            <col>Open</col>
        </pt12>
        <pt13>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Final Res. Ck.</col>
        </pt13>

        <pt14>
            <col>Open</col>
            <col>OK to Close</col>
            <col>Close</col>
        </pt14>
        <pt15>
            <col>OK to Close</col>
            <col>Close</col>
        </pt15>
        <pt16>
            <col>Open</col>
            <col>Protect</col>
            <col>OK to Close</col>
            <col>Close</col>
        </pt16>
        <pt17>
            <col>Protect</col>
            <col>OK to Close</col>
            <col>Close</col>
        </pt17>
        <pt18>
            <col>Open</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Inspect</col>
            <col>Leak Check</col>
            <col>Seal</col>
        </pt18>
        <pt19>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Inspect</col>
            <col>Leak Check</col>
            <col>Seal</col>
        </pt19>
        <pt20>
            <col>Open</col>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Seal</col>
        </pt20>
        <pt21>
            <col>OK to Close</col>
            <col>Close</col>
            <col>Seal</col>
        </pt21>
        <pt22>
            <col>Open</col>
            <col>Prep Cutout</col>
            <col>DVI Cutout</col>
            <col>Check Cond.</col>
            <col>OK to Close</col>
            <col>Close</col>
        </pt22>
    </xsl:variable>

    <xsl:variable name="genTextColor">
        <xsl:value-of select="'#6666aa'"/>
    </xsl:variable>
    <xsl:variable name="srcTextColor">
        <xsl:value-of select="'#00b050'"/>
    </xsl:variable>
    <xsl:variable name="sceptreTextColor">
        <xsl:value-of select="'#008888'"/>
    </xsl:variable>
    <xsl:variable name="lookupTextColor">
        <xsl:value-of select="'#880088'"/>
    </xsl:variable>
    <!--from original plug-in end    -->

</xsl:stylesheet>