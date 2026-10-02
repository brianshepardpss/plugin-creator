package shop

final case class Money(cents: Long) {
  def +(other: Money): Money = Money(cents + other.cents)
  override def toString: String = f"$$${cents / 100}%d.${cents % 100}%02d"
}

object Money {
  val zero: Money = Money(0L)

  implicit val moneyOrdering: Ordering[Money] = Ordering.by(_.cents)

  implicit class MoneyOps(private val n: Int) extends AnyVal {
    def dollars: Money = Money(n.toLong * 100)
  }
}
