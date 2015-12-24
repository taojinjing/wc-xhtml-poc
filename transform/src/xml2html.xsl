<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="workcard">
        <html xmlns="http://www.w3.org/1999/xhtml"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://www.w3.org/1999/xhtml file:/../resource/xhtml1-strict.xsd">
            <head>
                <title>sample xhtml workcard</title>
            </head>
            <body>
                <xsl:apply-templates/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="*">
        <div>
            <xsl:attribute name="class">
                <xsl:value-of select="name()"/>
            </xsl:attribute>
            <xsl:for-each select="@*" >
                <span>
                    <xsl:attribute name="class">
                        <xsl:value-of select="name()"/>
                    </xsl:attribute>
                    <xsl:value-of select="."/>
                </span>
            </xsl:for-each>
            <xsl:apply-templates/>
        </div>
    </xsl:template>

</xsl:stylesheet>