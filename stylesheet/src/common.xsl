<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:sf="http://www.syntext.com/Extensions/Functions"
                xmlns:fo="http://www.w3.org/1999/XSL/Format">
  <!--If 'true' always show  change.mark highlights, otherwise functionality is switched OFF -->
  <xsl:param name="change.mark.enable" select="'true'"/>              
                
  <!-- Shared parameters for setting colors for change marks-->
  <xsl:param name="change.mark.color.add" select="'#ff99ff'"/>
  <xsl:param name="change.mark.color.delete" select="'#ffcc66'"/>
  <xsl:param name="change.mark.color.modify" select="'#ffff99'"/>
  
  <xsl:template name="process-common-attributes-and-children">
    <xsl:call-template name="process-common-attributes"/>
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template name="process-common-attributes">
    <xsl:choose>
      <xsl:when test="@xml:lang">
        <xsl:attribute name="xml:lang">
          <xsl:value-of select="@xml:lang"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:when test="@lang">
        <xsl:attribute name="xml:lang">
          <xsl:value-of select="@lang"/>
        </xsl:attribute>
      </xsl:when>
    </xsl:choose>
  </xsl:template>
    
  <xsl:template name="indicateChanges">
    <xsl:if test="@changeType and $change.mark.enable = 'true'">
    <!-- change background color depends of @change attribute value -->
      <xsl:choose>
        <xsl:when test="@changeType='delete'">
            <xsl:attribute name="background-color"><xsl:value-of select="$change.mark.color.delete"/></xsl:attribute>
            <xsl:attribute name="text-decoration">line-through</xsl:attribute>
        </xsl:when>
        <xsl:when test="@changeType='modify'">
            <xsl:attribute name="background-color"><xsl:value-of select="$change.mark.color.modify"/></xsl:attribute>
        </xsl:when>
        <xsl:when test="@changeType='add'">
            <xsl:attribute name="background-color"><xsl:value-of select="$change.mark.color.add"/></xsl:attribute>
        </xsl:when>
      </xsl:choose>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>
