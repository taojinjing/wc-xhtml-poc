<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:sf="http://www.syntext.com/Extensions/Functions"
                version="1.0">

    <!--_________________________________________________________________________-->
    <!--         *************Steps*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step1']|h:div[@class='step2']|h:div[@class='step3']|h:div[@class='step4']|h:div[@class='step5']|h:div[@class='step6']|h:div[@class='step7']|h:div[@class='step8']" mode="step-numbers">
        <xsl:if
                test="parent::h:div[@class='step5'] or parent::h:div[@class='step4'] or parent::h:div[@class='step3'] or parent::h:div[@class='step2'] or parent::h:div[@class='step1']">
            <xsl:apply-templates
                    select="parent::h:div[@class='step5'] or parent::h:div[@class='step4'] or
               parent::h:div[@class='step3'] or parent::h:div[@class='step2'] or parent::h:div[@class='step1']"
                    mode="step-numbers"/>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="self::h:div[@class='step1']">
                <xsl:number format="1" />. </xsl:when>
            <xsl:when test="self::h:div[@class='step2']">
                <xsl:number  format="A" />. </xsl:when>
            <xsl:when test="self::h:div[@class='step3']">
                <xsl:number format="(1)"/>
            </xsl:when>
            <xsl:when test="self::h:div[@class='step4']">
                <xsl:number format="(a)"/>
            </xsl:when>
            <xsl:when test="self::h:div[@class='step5']">
                <xsl:number format="1)"/>
            </xsl:when>
            <xsl:when test="self::h:div[@class='step6']">
                <xsl:number format="a)"/>
            </xsl:when>
            <xsl:when test="self::h:div[@class='step7']">
                <xsl:number format="1."/>
            </xsl:when>
            <xsl:when test="self::h:div[@class='step8']">
                <xsl:number format="a."/>
            </xsl:when>
        </xsl:choose>
    </xsl:template>


    <xsl:template name="backorder">
        <xsl:param name="in"/>
        <xsl:if test="$in">
            <xsl:apply-templates select="$in[last()]"/>
            <xsl:call-template name="backorder">
                <xsl:with-param name="in" select="$in[position() &lt; last()]"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <xsl:template name="steps">
        <xsl:param name="format"/>
        <fo:block>
            <xsl:call-template name="indicateChanges"/>
            <xsl:if test="@dmidreftype='link' or @dmidreftype='linkStepContinue'">
                <xsl:attribute name="background-color">#C8DCFF</xsl:attribute>
            </xsl:if>
            <xsl:if test="@dmidreftype='adapt' or @dmidreftype='adaptStepContinue'">
                <xsl:attribute name="background-color">#C8FFC8</xsl:attribute>
            </xsl:if>
            <xsl:if test="text[1]/preceding-sibling::node()">
                <fo:block start-indent="0pt">
                    <xsl:call-template name="backorder">
                        <xsl:with-param name="in" select="h:div[@class='text'][1]/preceding-sibling::node()"/>
                    </xsl:call-template>
                </fo:block>
            </xsl:if>
            <fo:list-block padding-top="0pt">
                <fo:list-item padding-top="1pt">
                    <fo:list-item-label end-indent="label-end()">
                        <fo:block padding-top="4pt" color="{$genTextColor}">
                            <xsl:choose>
                                <xsl:when test="$format = '1'">
                                    <xsl:number format="1" />. </xsl:when>
                                <xsl:when test="$format = 'A'">
                                    <xsl:number format="A" />. </xsl:when>
                                <xsl:when test="$format = '(1)'">
                                    <xsl:number format="(1)" />
                                </xsl:when>
                                <xsl:when test="$format = '(a)'">
                                    <xsl:number format="(a)" />
                                </xsl:when>
                                <xsl:when test="$format = '1)'">
                                    <xsl:number format="1)" />
                                </xsl:when>
                                <xsl:when test="$format = 'a)'">
                                    <xsl:number format="a)" />
                                </xsl:when>
                                <xsl:when test="$format = '1.'">
                                    <xsl:number format="1." />
                                </xsl:when>
                                <xsl:when test="$format = 'a.'">
                                    <xsl:number format="a." />
                                </xsl:when>
                            </xsl:choose>
                        </fo:block>
                    </fo:list-item-label>
                    <fo:list-item-body start-indent="body-start()" end-indent="0pt">
                        <fo:block>
                            <xsl:choose>
                                <xsl:when test="h:div[@class='text']">
                                    <xsl:apply-templates select="h:div[@class='text'][1]"/>
                                    <xsl:apply-templates select="h:div[@class='text'][1]/following-sibling::*"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:apply-templates/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </fo:block>
                    </fo:list-item-body>
                </fo:list-item>
            </fo:list-block>
        </fo:block>
    </xsl:template>


    <!--_________________________________________________________________________-->
    <!--         *************Step1*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step1']">
        <xsl:call-template name="steps">
            <xsl:with-param name="format">1</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--_________________________________________________________________________-->
    <!--         *************Step2*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step2']">
        <xsl:call-template name="steps">
            <xsl:with-param name="format">A</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--_________________________________________________________________________-->
    <!--         *************Step3*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step3']">
        <xsl:call-template name="steps">
            <xsl:with-param name="format">(1)</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--_________________________________________________________________________-->
    <!--         *************Step4*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step4']">
        <xsl:call-template name="steps">
            <xsl:with-param name="format">(a)</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--_________________________________________________________________________-->
    <!--         *************Step5*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step5']">
        <xsl:call-template name="steps">
            <xsl:with-param name="format">1)</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--_________________________________________________________________________-->
    <!--         *************Step6*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step6']">
        <xsl:call-template name="steps">
            <xsl:with-param name="format">a)</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--_________________________________________________________________________-->
    <!--         *************Step7*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step7']">
        <xsl:call-template name="steps">
            <xsl:with-param name="format">1.</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--_________________________________________________________________________-->
    <!--         *************Step7*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='step8']">
        <xsl:call-template name="steps">
            <xsl:with-param name="format">a.</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--_________________________________________________________________________-->
    <!--         *************Para*************             -->
    <!--_________________________________________________________________________-->
    <xsl:template match="h:div[@class='para']">
        <fo:block padding-top="4pt">
            <xsl:call-template name="indicateChanges"/>
            <xsl:choose>
                <xsl:when test="*">
                    <xsl:apply-templates/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy-of select="node()"/>
                </xsl:otherwise>
            </xsl:choose>
        </fo:block>
    </xsl:template>

</xsl:stylesheet>