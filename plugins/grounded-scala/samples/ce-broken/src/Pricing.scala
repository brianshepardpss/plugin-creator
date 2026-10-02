package fakeshop

import scala.concurrent.Future

object Pricing:

  def lineTotal(l: Line): BigDecimal = l.unitPrice * l.qty

  // Seeded error 2: Scala 2 procedure syntax (dropped in Scala 3).
  def logLine(l: Line) {
    println(l.show)
  }

  // Seeded error 3: a Future where the signature promises cats-effect IO.
  def orderTotal(o: Order): cats.effect.IO[BigDecimal] =
    Future {
      o.lines.map(lineTotal).sum
    }
