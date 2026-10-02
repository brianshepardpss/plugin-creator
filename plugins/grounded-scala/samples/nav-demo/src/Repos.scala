package navdemo

final case class UserId(value: Long)
final case class User(id: UserId, name: String)
final case class Order(id: Long, owner: UserId)

class UserRepo(data: Map[UserId, User]):
  def findById(id: UserId): Option[User] = data.get(id)
  def all: List[User] = data.values.toList

/** Decoy: same method name, different class. Not a caller of UserRepo.findById. */
class OrderRepo(data: Map[Long, Order]):
  def findById(id: Long): Option[Order] = data.get(id)

/** Alias used by some call sites. */
type Users = UserRepo

object Fixtures:
  val alice = User(UserId(1), "Test User A (fake)")
  val bob = User(UserId(2), "Test User B (fake)")
  val users: Users = UserRepo(Map(alice.id -> alice, bob.id -> bob))
  val orders = OrderRepo(Map(10L -> Order(10L, alice.id)))
