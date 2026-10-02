package fakeshop

/** Clearly fake domain for the Grounded Scala sample. */
final case class Order(id: String, customer: String, lines: List[Line])
final case class Line(sku: String, qty: Int, unitPrice: BigDecimal)

/** A tiny type class: render a value for a log line. */
trait Show[A]:
  def show(a: A): String

object Show:
  def apply[A](using s: Show[A]): Show[A] = s

  given Show[Line] with
    def show(l: Line): String = s"${l.qty} x ${l.sku} @ ${l.unitPrice}"

extension [A](a: A)(using s: Show[A])
  def show: String = s.show(a)
