package org.altbeacon.beaconreference;

import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import java.net.NetworkInterface;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

public class SplashActivity extends Activity {

    private static String uniqueID = null;

    private static String token = null;

    private static final String PREF_UNIQUE_ID = "PREF_UNIQUE_ID";
    public synchronized static String id(Context context) {
        if (uniqueID == null) {
            SharedPreferences sharedPrefs = context.getSharedPreferences(
                    PREF_UNIQUE_ID, Context.MODE_PRIVATE);
            uniqueID = sharedPrefs.getString(PREF_UNIQUE_ID, null);
            if (uniqueID == null) {
                uniqueID = UUID.randomUUID().toString();
                SharedPreferences.Editor editor = sharedPrefs.edit();
                editor.putString(PREF_UNIQUE_ID, uniqueID);
                editor.commit();
            }
        }    return uniqueID;
    }

    public static String getDevId(){
        return uniqueID;
    }

    public static String getToken(){return token;}

    @SuppressLint("MissingPermission")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.splash);
            id(this.getApplicationContext());
        }
    }

    public void onRegisterClicked(View view) {

    }

    public void onLogInClicked(View view){

    }

    public void onAnonymousClicked(View view){
        RequestQueue volleyQueue = Volley.newRequestQueue(SplashActivity.this);
        String url = "https://tfg-u3xd.onrender.com/login/anonymous";
        JSONObject entrada = new JSONObject();
        TextView t = (TextView) findViewById(R.id.mac);
        try{
            entrada.put("mac_addr",uniqueID);
        } catch(JSONException e){
            e.printStackTrace();
        }
        t.setText(uniqueID);


        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST,url,entrada
                ,(Response.Listener<JSONObject>) response-> {
            String rsp = response.toString();
            t.setText(rsp);
            Intent myIntent = new Intent(this, MonitoringActivity.class);
            token = response.toString();
            this.startActivity(myIntent);
            try{
                Log.d("respuesta", response.getString("message"));
            }
            catch (JSONException e){
                e.printStackTrace();
            }
        },
                (Response.ErrorListener) error -> {
                    // make a Toast telling the user
                    // that something went wrong
                    Toast.makeText(SplashActivity.this, "Some error occurred!", Toast.LENGTH_LONG).show();
                    // log the error message in the error stream
                    Log.e("MainActivity", "loadDogImage error: ${error.localizedMessage}");
                });
        volleyQueue.add(jsonObjectRequest);
    }

}