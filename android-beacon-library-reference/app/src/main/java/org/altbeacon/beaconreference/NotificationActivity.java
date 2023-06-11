package org.altbeacon.beaconreference;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.TaskStackBuilder;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

public class NotificationActivity extends Activity {
    public String room_name;
    public Double n_personas;
    private static ScheduledExecutorService executor;
    private static ScheduledFuture<?> scheduledFuture;
    private boolean isEventOccurred = false;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_notification);
        executor = Executors.newScheduledThreadPool(1);
    }
    @Override
    public void onResume(){
        super.onResume();
    }

    public void onNotClicked(View view){
        EditText input = (EditText) findViewById(R.id.roomNameText);
        EditText number = (EditText) findViewById(R.id.number_of_people);
        if(number.getText().toString().equals("Baja")){
            this.n_personas = 0.50;
        }
        else if (number.getText().toString().equals("Media")){
            this.n_personas = 0.75;
        }
        else{
            this.n_personas = 1.0;
        }
        this.room_name = input.getText().toString();


        Notification_aux repeatTask = new Notification_aux(this,room_name,n_personas);
        scheduledFuture = executor.scheduleAtFixedRate(repeatTask,0, 5, TimeUnit.MINUTES);
    }
    public static void stopScheduledTask(){
        if (scheduledFuture != null) {
            scheduledFuture.cancel(true);
        }
        if (executor != null) {
            executor.shutdown();
        }
    }


}