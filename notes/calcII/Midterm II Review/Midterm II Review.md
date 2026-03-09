The key to this part of the course is mastering a few procedures dealing with integrals, and recognizing when to use them. Below is an itemized list of the sections covered since the last exam, each with a collection of associated problems. This table of contents should also serve as a guide to thought process: when faced with a new integral, use this as a hierarchy of methods to try:

- First, try it directly using [[§5.4 Indefinite Integrals#^5fcf9e|Power Rule]] and [[§5.4 Indefinite Integrals#^adaaae|trigonometric substitutions]] 
- Then look for a composition of functions to use [[§5.5 The Substitution Rule]] on
- If there's a product of functions, use [[§7.1 Integration by Parts]] 
- If the integrand is solely trigonometric functions, [[§7.2 Trigonometric Integration]]
- If there's a quadratic under a radical, [[§7.3 Trigonometric Substitution]]
- Finally, for ratios of polynomials, [[§7.4 Partial Fraction Decomposition]] 
The other section to review are on [[§7.8 Improper Integrals]] 
## $u$-Substitution
Thing to remember: Look for a composition of functions, and differentiate the inner function.

> [!example] Problem
> When integrating $\int x^3\left(x^4+1\right)^2 d x$ using the substitution method, we would begin by letting $u$ equal to which of the following:
> - $x^3$
> - $x\left(x^4+1\right)$
> - $\left(x^4+1\right)^2$
> - $x^4+1$
>
>> [!success]- Solution
>> Inner function here is $x^4 + 1$.

> [!example] Problem
> Evaluate the integral:
> $$
> \int \frac{\left ( \ln(x) \right )^6}{x}dx
> $$
>> [!success]- Solution
>> $\displaystyle \frac17 \ln(x)^7 + C$

> [!example] Problem
> Using the substitution $u=x^2-3$, what is $\int_{-1}^4 x\left(x^2-3\right)^5 d x$,  equal to?
>> [!success]- Solution
>> $\displaystyle \int_{-2}^{13} u^5 du$

## Integration by Parts
Thing to remember:
$$
\int u dv = uv - \int v du
$$
Here's some [review](https://www.math.ucdavis.edu/ kouba/CalcTwoDIRECTORY/intbypartsdirectory/IntByParts.html)
> [!example] Problem
> Compute
> $$
> \int x \cos(x) dx
> $$
>> [!success]- Solution
>> $x \sin (x) + \cos (x) + C$

> [!example] Problem
> Compute
> $$
> \int (\ln(x))^2 dx
> $$
>> [!success]- Solution
>> Do this by $u$-substitution first: let $u = \ln(x)$ and $du = 1/x dx$
>> $$\int u^2 (e^u du)$$
>> Do integration by parts twice to get:
>> $$x ((\ln(x))^2-2 \ln(x)+2) + C$$

> [!example] Problem
> Evaluate the definite integral:
> $$
> \int_0^1 x^2 e^x dx
> $$
>> [!success]- Solution
>> $e-2$

> [!example] Problem
> Let $f$ be a differentiable function such that $$\int f(x) \sin x d x=-f(x) \cos x+\int 4 x^3 \cos x d x$$. What is a possibility for $f(x)$?
>> [!success]- Solution
>> $x^4$

## Trigonometric Integration
Thing to remember:
$$
\sin^2 (x) + \cos^2(x) = 1 \quad \text{ and } \quad \tan^2 (x) + 1 = \sec^2 (x)
$$
Look for *odd* powers on $\sin, \cos$ or factors of $\sec^2$ and $\sec \tan$. Here's some [review](https://www.math.ucdavis.edu/ kouba/CalcTwoDIRECTORY/trigintdirectory/TrigInt.html) and some [more](https://tutorial.math.lamar.edu/classes/calcii/integralswithtrig.aspx)


> [!example] Problem
> Integrate:
> $$
> \int (\sin(x) + \cos(x))^2 dx
> $$
>> [!success]- Solution
>> Expand out the polynomial to get:
>> $$\underbrace{\sin^2(x) + \cos^2(x)}_{=1} + 2 \sin(x) \cos(x)$$
>> The rest should be just $u$-substitution:
>> $$x - 2\sin^2(x) + C$$

> [!example] Problem
> Compute:
> $$
> \int\left(\sec ^2 x\right) \sqrt{5+\tan x} d x
> $$
>> [!success]- Solution
>> Eyes should light up at the $\sec^2(x)$ term hanging out there, this is just a $u$-sub on $u = \tan(x)$. 
> $$= \frac23 (5 + \tan(x))^{3/2} + C$$

## Trigonometric Substitution
Thing to remember:
$$
\begin{array}{|c|c|c|}
\hline
\text{Expression} & \text{Substitution} & \text{Identity} \\ \hline
\sqrt{a^2 - x^2} & \displaystyle x = a \sin \theta, \theta \in \left [ \frac{-\pi}{2}, \frac\pi2 \right ] & 1 - \sin^2 \theta = \cos^2 \theta\\ \hline 
\sqrt{a^2 + x^2} & \displaystyle x = a \tan \theta, \theta \in \left ( \frac{-\pi}{2}, \frac\pi2 \right ) & 1 + \tan^2 \theta = \sec^2 \theta \\ \hline
\sqrt{x^2 - a^2} & \displaystyle x = a \sec\theta,  \theta \in \left [ 0, \frac\pi2 \right ) \text{ or } \in \left [ \pi, \frac{3\pi}{2} \right ) & \sec^2\theta - 1 = \tan^2 \theta \\ 
\hline
\end{array}
$$
To complete problems, use a triangle. Here's some [review](https://tutorial.math.lamar.edu/classes/calcii/TrigSubstitutions.aspx) and some [more](https://www.math.ucdavis.edu/ kouba/CalcTwoDIRECTORY/trigsubdirectory/TrigSub.html)

> [!example] Problem
> Compute
> $$
> \int \sqrt{1 - x^2} dx
> $$
>> [!success]- Solution
>> Deceptively tricky! Make the substitution $x = \sin(\theta)$ to get the integrand:
>> $$\int \cos^2(\theta) = \frac12 \int 1 + \cos(2\theta) d \theta$$
>> with the latter equality from the *power reduction* formula. Integrating gives:
>> $$\frac12 \theta + \frac14 \sin(2\theta) = \frac12 \theta + \frac12 \sin (\theta) \cos (\theta )$$
>> Reversing the subsitution using the Pythagorean theorem gives:
>> $$\boxed{\frac12 \arcsin(x) + \frac12 x \sqrt{1-x^2} + C}$$

> [!example] Problem
> Compute
> $$
> \int_0^1 \sqrt{x^2-2 x+1} d x
> $$
>> [!success]- Solution
>> $\frac12$

> [!example] Problem
> Compute
> $$
> \int_0^1\left(4-x^2\right)^{-\frac{3}{2}} d x=
> $$
>> [!success]- Solution
>> Make the subsitution $x=2 \sin \theta \Rightarrow d x=2 \cos \theta d \theta$.
>> $$\int_0^1\left(4-x^2\right)^{-3 / 2} d x=\int_0^{\pi / 6} \frac{2 \cos \theta}{8 \cos ^3 \theta} d \theta=\frac{1}{4} \int_0^{\pi / 6} \sec ^2 \theta d \theta=\left.\frac{1}{4} \tan \theta\right|_0 ^{\pi / 6}=\frac{1}{4} \cdot \frac{\sqrt{3}}{3}=\frac{\sqrt{3}}{12}$$

## Partial Fraction Decomposition
Thing to remember: decompose:
$$
\frac{p(x)}{q(x)} = s(x) + \frac{r(x)}{q(x)}
$$
using polynomial long division. Then remember: “constants for distinct linear factors and their repetitions, linear terms for the quadratics.” Here's some [practice](https://www.math.ucdavis.edu/ kouba/CalcTwoDIRECTORY/partialfracdirectory/PartialFrac.html)

> [!example] Problem
> Integrate:
> $$
> \int \frac{2x + 3}{x^2 - 9}
> $$
>> [!success]- Solution
>> $$ \frac12 \left (  3\ln (3-x) + \ln (x+3) \right )$$

> [!example] Problem
> Compute:
> $$
> \int \frac{1}{x^2 - 6x + 8} dx
> $$
> [!success]- Solution
> $$
> \frac12 \left ( \ln \left | x - 4 \right | - \ln \left | x - 2 \right | \right )
> $$

> [!example] Problem
> Compute the following: $$
> \int_0^1 \frac{5 x+8}{x^2+3 x+2} d x
> $$
> [!success]- Solution
> $\ln(18)$

## Improper Integrals
\begin{aun}
Thing to remember: does the integral have an infinite bound? if so, replace with $b$ and evaluate the limit $\lim_{b \to \infty}$. Does the function have discontinuities on the domain of integration? If so, approach with limits from either side. If any limit diverges, the integral diverges.
\end{aun}

> [!example] Problem
> Evaluate the integral:
> $$
> \int_1^\infty e^{-3x}dx
> $$
> [!success]- Solution
> $\displaystyle \frac{1}{3e^3}$

> [!example] Problem
> Compute the integral
> $$
> \int_0^\infty x^2 e^{-x^3} dx
> $$

> [!success]- Solution
> $$
> \lim_{b \to \infty} \left [ -\frac13 e^{-x^3}  \right ]^b_0 = \frac13
> $$

## The Grab Bag
\begin{aun}
If I sort these into a category, it’ll give away the answer
\end{aun}

> [!example] Problem
> [True or False] Integrals of the form:
> $$
> \int_0^\infty f(x)dx
> $$
> have a finite numerical value.
> [!success]- Solution
> False

> [!example] Problem
> Evaluate the integral:
> $$
> \int\left(4 x^2-1\right) \cos \left(4 x^3-3 x\right) d x
> $$
> [!success]- Solution
> $=-\frac{1}{3} \sin \left(3 x-4 x^3\right)+\text { constant }$

> [!example] Problem
> Compute the integral:
> $$
> \int_0^1 \frac{x^2}{x^2 + 1}
> $$
> **HINT:** what’s the derivative of $\arctan$?
> [!success]- Solution
> $1 - \pi/4$

> [!example] Problem
> Compute $$
> \int_1^e\left(\frac{x^2-1}{x}\right) d x=
> $$
> [!success]- Solution
> $\frac12 (e^2 - 3)$; split this one into two integrals

> [!example] Problem
> If $\frac{dy}{dx} = \sin(x) \cos^2 (x)dx$ and $y = 0$ when $x = \frac{\pi}{2}$, what is $y$ when $x$ is 0?

> [!success]- Solution
> Using the antiderivative 
> $$
> y(x) = -\frac13 \cos^3 (x) + 0 \quad \text{ we have } \quad-\frac13
> $$

> [!example] Problem
> Compute
> $$
> \int_0^1 \sqrt{x} (x+1) dx
> $$
> [!success]- Solution
> $\frac{16}{15}$

> [!example] Problem
> Compute
> $$
> \int_1^{\infty} \frac{x}{\left(1+x^2\right)^2} d x
> $$
> [!success]- Solution
> $$
> \lim_{b \to \infty} \left [ \frac14 - \frac{1}{2(1-b^2)}  \right ] = \frac14
> $$

> [!example] Problem
> Compute 
> $$
> \int \sin^3 (x)dx
> $$
> [!success]- Solution
> Odd power of $\sin$ is good news, at least!
> $$
> \int( 1-\cos^2 (x)) \sin(x)dx = \int u^2 - 1 du ...
> $$
> Follow out the algebra to get 
> $$
> -\cos(x) + \frac13 \cos^3(x) + C
> $$

> [!example] Problem
> Compute
> $$
> \int \frac{\cos^2(x)}{1 + \sin(x)}
> $$
> [!success]- Solution
> Conjugate the denominator:
> $$
> \int \frac{\cos^2(x) (1-\sin(x))}{1- \sin^2(x)} = \int \frac{\cos^2(x) (1-\sin(x))}{\cos^2(x)} = \int 1- \sin(x) dx
> $$
> Finish it out from here to get:
> $$
> x + \cos(x) + C
> $$

> [!example] Problem
> Compute 
> $$
> \int \frac{d x}{(x-1)(x+3)}
> $$

> [!success]- Solution
> Use partial fractions
> $$
> \frac14 \ln \left | \frac{x-1}{x+3} \right | + C
> $$

> [!example] Problem
> Compute $$
> \int_4^{\infty} \frac{-2 x}{\sqrt[3]{9-x^2}} d x
> $$
> [!success]- Solution
> DNE by comparison to $x^{2/3}$

> [!example] Problem
> Compute $$
> \int \frac{\left(x^2-1\right)^{3 / 2}}{x} d x
> $$
> [!success]- Solution
> The radical should suggest a trig substitution:
> $$
> \int \frac{\left(x^2-1\right)^{3 / 2}}{x} d x = \int \frac{(\sqrt{x^2 - 1})^3}{x} dx = \int \frac{\tan^3 \theta}{\sec \theta}
> $$
> over the substitution $x = \sec(\theta)$. 
> $$
> \cdots = \frac13 \sqrt{x^2 - 1} (x^2 -4 ) + \arctan \left ( \sqrt{x^2 - 1} \right ) + C
> $$

> [!example] Problem
> Integrate $$
> \int \frac{x}{\sqrt{x^2+4 x+5}} d x
> $$
> [!success]- Solution
> Do a substitution after completing the square:
> $$
> x^2 + 4x + 5 = (x+2)^2 + 1
> $$
> Get:
> $$
> \sqrt{x^2+4 x+5} - 2\ln \left | \sqrt{x^2+4 x+5} + x + 2 \right | + C
> $$

> [!example] Problem
> Compute 
> $$
> \int x^3 \ln (5x) dx
> $$

> [!success]- Solution
> This is parts- get:
> $$
> \frac14 x^4 \ln \left ( 5x \right ) - \frac{x^4}{16} + C
> $$

> [!example] Problem
> Compute 
> $$
> \int x \sin (x) \cos (x)dx
> $$
> [!success]- Solution
> Tricky tricky- see that:
> $$
> \int x \sin(x) \cos(x) dx = \frac12 \int x \sin(2x)dx
> $$
> Apply parts from here to get:
> $$
> \frac12 \left ( - \frac12 x \cos(2x) + \frac14 \sin(2x) \right ) + C
> $$

> [!example] Problem
> Integrate
> $$
> \int \frac{x^4 + x^3 + x^2 + 1}{x^2 + x -2}
> $$
> [!success]- Solution
> Start with polynomial long division:
> $$
> \frac{x^4 + x^3 + x^2 + 1}{x^2 + x -2} = x^2 + 3 + \frac{-3x+7}{x^2 + x -2}
> $$
> Continue by partial fractions:
> $$
> = \frac13 x^3 + 3x + \frac43 \ln \left | x-1 \right | - \frac{13}{3} \ln \lrabs {x+2} + C
> $$