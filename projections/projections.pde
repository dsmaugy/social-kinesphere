import netP5.*;
import oscP5.*;

import java.net.InetAddress;
import java.net.UnknownHostException;

OscP5 oscP5;

enum MachineID {
  VOID1, VOID2, VOID3, VOID4, UNKNOWN
}
MachineID currentMachine = MachineID.UNKNOWN;

void setup() {
  size(400, 400);
  try {
    String hostname = InetAddress.getLocalHost().getHostName();
    println("hostname: " + hostname);

    if (hostname.startsWith("void")) {
      int hostID = Character.getNumericValue(hostname.charAt(4));
      currentMachine = MachineID.values()[hostID];
    }

    println("machine ID: " + currentMachine);
  }

  catch (UnknownHostException e) {
    println("Unknown Host");
    exit();
  }

  oscP5 = new OscP5(this, 6123);
}


void draw() {
  circle(25, 10, 10);
}

void oscEvent(OscMessage msg) {
  println("Received OSC message:");
  println("Address Pattern: " + msg.addrPattern());
  for (int i = 0; i < msg.typetag().length(); i++) {
    println("Arg " + i + ": " + msg.get(i).floatValue());
  }
}
