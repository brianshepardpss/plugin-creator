package shop

import scala.language.implicitConversions

trait Priced[A] {
  def price(a: A): Money
}

object Priced {
  def apply[A](implicit p: Priced[A]): Priced[A] = p
}

final case class Item(sku: String, unit: Money, qty: Int)

object Item {
  implicit val itemPriced: Priced[Item] = new Priced[Item] {
    def price(i: Item): Money = Money(i.unit.cents * i.qty)
  }
  implicit def fromTuple(t: (String, Money)): Item = Item(t._1, t._2, 1)
}

object Cart {
  import Money._

  def total[A: Priced](as: Seq[A]): Money =
    as.map(Priced[A].price).foldLeft(Money.zero)(_ + _)

  def priciest[A](as: Seq[A])(implicit p: Priced[A]): Option[A] =
    if (as.isEmpty) None else Some(as.maxBy(a => p.price(a)))

  def describe(items: Item*) {
    items.foreach { i => println(s"${i.qty} x ${i.sku}") }
  }

  def main(args: Array[String]): Unit = {
    val items: Seq[Item] = Seq(Item("SKU-PEN", 3.dollars, 2), ("SKU-PAD", 5.dollars))
    describe(items: _*)
    println(s"total=${total(items)} priciest=${priciest(items).map(_.sku).getOrElse("-")}")
    val sym = 'legacy
    println(sym.name)
  }
}
