import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Groups = () => {
  const [groups, setGroups] = useState([]);
  const [pendingInvitations, setPendingInvitations] = useState([]);
  const [newGroupName, setNewGroupName] = useState('');
  const [inviteUsername, setInviteUsername] = useState('');
  const [selectedGroupId, setSelectedGroupId] = useState(null);
  const [selectedGroupMembers, setSelectedGroupMembers] = useState(null);
  const [selectedGroupName, setSelectedGroupName] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const fetchGroups = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/groups/my', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch groups');
      const data = await response.json();
      setGroups(data);
    } catch (err) {
      setError('Failed to load groups');
    }
  };

  const fetchPendingInvitations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/groups/invitations/pending', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch invitations');
      const data = await response.json();
      setPendingInvitations(data);
    } catch (err) {
      setError('Failed to load invitations');
    }
  };

  useEffect(() => {
    fetchGroups();
    fetchPendingInvitations();
  }, []);

  const createGroup = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/groups/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newGroupName }),
      });
      if (!response.ok) throw new Error('Failed to create group');
      setSuccess('Group created successfully!');
      setNewGroupName('');
      fetchGroups();
    } catch (err) {
      setError('Failed to create group');
    }
  };

  const inviteUser = async (e) => {
    e.preventDefault();
    if (!selectedGroupId) {
      setError('Please select a group first');
      return;
    }
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/groups/${selectedGroupId}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ username: inviteUsername }),
      });
      if (!response.ok) throw new Error('Failed to invite user');
      setSuccess('Invitation sent successfully!');
      setInviteUsername('');
    } catch (err) {
      setError('Failed to invite user');
    }
  };

  const acceptInvitation = async (invitationId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/groups/invitations/${invitationId}/accept`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to accept invitation');
      setSuccess('Successfully joined the group!');
      fetchGroups();
      fetchPendingInvitations();
    } catch (err) {
      setError('Failed to accept invitation');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Groups
        </h1>

        {error && (
          <div className="bg-red-500 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-500 text-white p-3 rounded mb-4">
            {success}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Create Group Form */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Create New Group</h2>
            <form onSubmit={createGroup} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Group Name
                </label>
                <input
                  type="text"
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  className="w-full p-2 rounded bg-gray-700 text-white"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
              >
                Create Group
              </button>
            </form>
          </div>

          {/* Invite User Form */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Invite User</h2>
            <form onSubmit={inviteUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Select Group
                </label>
                <select
                  value={selectedGroupId || ''}
                  onChange={(e) => setSelectedGroupId(e.target.value)}
                  className="w-full p-2 rounded bg-gray-700 text-white"
                  required
                >
                  <option value="">Select a group</option>
                  {groups
                    .filter((group) => group.is_admin)
                    .map((group) => (
                      <option key={group.id} value={group.id}>
                        {group.group_name}
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={inviteUsername}
                  onChange={(e) => setInviteUsername(e.target.value)}
                  className="w-full p-2 rounded bg-gray-700 text-white"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
              >
                Send Invitation
              </button>
            </form>
          </div>
        </div>

        {/* My Groups */}
        <div className="mt-8 bg-gray-800 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">My Groups</h2>
          {groups.length === 0 ? (
            <p className="text-gray-400">You're not a member of any groups yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {groups.map((group) => (
                <div
                  key={group.id}
                  className="bg-gray-700 p-4 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors"
                  onClick={async () => {
                    try {
                      const token = localStorage.getItem('access_token');
                      const response = await fetch(`http://localhost:8000/groups/${group.id}/members`, {
                        headers: {
                          Authorization: `Bearer ${token}`,
                        },
                      });
                      if (!response.ok) throw new Error('Failed to fetch group members');
                      const members = await response.json();
                      setSelectedGroupMembers(members);
                      setSelectedGroupName(group.group_name);
                    } catch (err) {
                      setError('Failed to load group members');
                    }
                  }}
                >
                  <h3 className="font-semibold">{group.group_name}</h3>
                  <p className="text-sm text-gray-400">
                    {group.is_admin ? 'Admin' : 'Member'}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Selected Group Members */}
          {selectedGroupMembers && (
            <div className="mt-6 bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-3">{selectedGroupName} - Members</h3>
              <div className="space-y-2">
                {selectedGroupMembers.map((member) => (
                  <div key={member.id} className="flex items-center justify-between p-2 rounded bg-gray-600">
                    <div>
                      <p className="font-medium">{member.username}</p>
                      <p className="text-sm text-gray-400">
                        {member.first_name} {member.last_name}
                      </p>
                    </div>
                    <span className="px-2 py-1 text-xs rounded bg-gray-500">
                      {member.is_admin ? 'Admin' : 'Member'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Pending Invitations */}
        <div className="mt-8 bg-gray-800 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Pending Invitations</h2>
          {pendingInvitations.length === 0 ? (
            <p className="text-gray-400">No pending invitations.</p>
          ) : (
            <div className="space-y-4">
              {pendingInvitations.map((invitation) => (
                <div
                  key={invitation.id}
                  className="bg-gray-700 p-4 rounded-lg flex items-center justify-between"
                >
                  <div>
                    <p>
                      <span className="font-semibold">{invitation.group_name}</span>
                    </p>
                    <p className="text-sm text-gray-400">
                      Invited by {invitation.inviter_username}
                    </p>
                  </div>
                  <button
                    onClick={() => acceptInvitation(invitation.id)}
                    className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                  >
                    Accept
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Groups;
